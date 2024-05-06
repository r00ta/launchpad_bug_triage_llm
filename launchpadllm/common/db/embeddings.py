from typing import Optional

from sqlalchemy import Select, delete, desc, insert, select
from sqlalchemy.sql.functions import count
from sqlalchemy.sql.operators import eq

from launchpadllm.common.db.repository import BaseRepository
from launchpadllm.common.db.sequences import EmbeddingSequence
from launchpadllm.common.db.tables import EmbeddingTable
from launchpadllm.common.models.base import ListResult
from launchpadllm.common.models.embeddings import Embedding


class EmbeddingsRepository(BaseRepository[Embedding]):
    async def get_next_id(self) -> int:
        stmt = select(EmbeddingSequence.next_value())
        return (
            await self.connection_provider.get_current_connection().execute(stmt)
        ).scalar()

    async def create(self, entity: Embedding) -> Embedding:
        stmt = (
            insert(EmbeddingTable)
            .returning(
                EmbeddingTable.c.id,
                EmbeddingTable.c.text_id,
                EmbeddingTable.c.embedding,
            )
            .values(id=entity.id, text_id=entity.text_id, embedding=entity.embedding)
        )
        result = await self.connection_provider.get_current_connection().execute(stmt)
        embedding = result.one()
        return Embedding(**embedding._asdict())

    async def find_by_id(self, id: int) -> Optional[Embedding]:
        stmt = select(
            "*").select_from(EmbeddingTable).where(EmbeddingTable.c.id == id)
        result = await self.connection_provider.get_current_connection().execute(stmt)
        embedding = result.first()
        if not embedding:
            return None
        return Embedding(**embedding._asdict())

    async def list(self, size: int, page: int) -> ListResult[Embedding]:
        total_stmt = select(count()).select_from(EmbeddingTable)
        total = (await self.connection_provider.get_current_connection().execute(total_stmt)).scalar()

        stmt = (
            select("*")
            .select_from(EmbeddingTable)
            .order_by(desc(EmbeddingTable.c.id))
            .offset((page - 1) * size)
            .limit(size)
        )

        result = await self.connection_provider.get_current_connection().execute(stmt)
        return ListResult[Embedding](
            items=[Embedding(**row._asdict()) for row in result.all()],
            total=total
        )

    async def update(self, entity: Embedding) -> Embedding:
        pass

    async def delete(self, id: int) -> None:
        await self.connection_provider.get_current_connection().execute(
            delete(EmbeddingTable).where(EmbeddingTable.c.id == id)
        )
