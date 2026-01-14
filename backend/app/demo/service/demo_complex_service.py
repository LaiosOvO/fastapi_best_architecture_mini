"""复杂业务逻辑服务层 - 演示跨表查询和服务依赖注入"""
from typing import Any, List
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.demo.model.demo import Demo
from backend.app.demo.model.document import Document
from backend.app.demo.model.location import Location
from backend.app.demo.schema.demo import GetDemoDetail, AddDemoParam
from backend.app.demo.schema.document import GetDocumentDetail, CreateDocumentParam
from backend.app.demo.schema.location import GetLocationDetail, CreateLocationParam
from backend.app.demo.service.demo_service import demo_service
from backend.app.demo.service.document_service import document_service
from backend.app.demo.service.location_service import location_service


class DemoComplexService:
    """复杂业务逻辑服务类 - 演示跨表查询和服务依赖注入"""

    @staticmethod
    async def get_demo_with_documents_and_locations(
        *,
        db: AsyncSession,
        demo_id: int
    ) -> dict[str, Any]:
        """
        根据ID查询demo，并根据demo中的document_ids查询相关文档和位置信息

        :param db: 数据库会话
        :param demo_id: demo ID
        :return: 包含demo、文档列表和位置列表的字典
        """
        # 获取demo信息
        demo = await demo_service.getById(db=db, id=demo_id)

        # 获取document_ids - 优先使用新添加的document_ids字段
        document_ids = demo.document_ids or []

        # 如果document_ids为空，尝试从metadata_json中查找
        if not document_ids and demo.metadata_json:
            if 'document_ids' in demo.metadata_json:
                document_ids = demo.metadata_json['document_ids']

        # 如果仍然为空，尝试从tags中查找
        if not document_ids and demo.tags:
            for tag in demo.tags:
                if tag.startswith('doc_id_'):
                    try:
                        doc_id = int(tag.replace('doc_id_', ''))
                        document_ids.append(doc_id)
                    except ValueError:
                        continue

        # 查询相关文档
        documents = []
        if document_ids:
            for doc_id in document_ids:
                try:
                    doc = await document_service.get(db=db, pk=doc_id)
                    documents.append(GetDocumentDetail.model_validate(doc))
                except ValueError:
                    # 文档不存在则跳过
                    continue

        # 查询相关位置 - 假设位置ID也存储在metadata中
        location_ids = []
        if demo.metadata_json and 'location_ids' in demo.metadata_json:
            location_ids = demo.metadata_json['location_ids']

        locations = []
        if location_ids:
            for loc_id in location_ids:
                try:
                    loc = await location_service.get(db=db, pk=loc_id)
                    locations.append(GetLocationDetail.model_validate(loc))
                except ValueError:
                    # 位置不存在则跳过
                    continue

        return {
            'demo': GetDemoDetail.model_validate(demo),
            'documents': documents,
            'locations': locations
        }

    @staticmethod
    async def create_demo_with_documents_and_locations(
        *,
        db: AsyncSession,
        demo_data: dict[str, Any],
        documents_data: List[dict[str, Any]],
        locations_data: List[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        创建demo以及关联的文档和位置

        :param db: 数据库会话
        :param demo_data: demo数据
        :param documents_data: 文档数据列表
        :param locations_data: 位置数据列表
        :return: 包含创建的demo、文档和位置的字典
        """
        # 创建demo
        demo_param = AddDemoParam(**demo_data)
        created_demo = await demo_service.create(db=db, obj=demo_param)

        # 收集创建的文档和位置ID
        created_documents = []
        created_locations = []
        document_ids = []
        location_ids = []

        # 创建文档
        for doc_data in documents_data:
            doc_param = CreateDocumentParam(**doc_data)
            created_doc = await document_service.create(db=db, obj=doc_param)
            created_documents.append(GetDocumentDetail.model_validate(created_doc))
            document_ids.append(created_doc.id)

        # 创建位置
        for loc_data in locations_data:
            loc_param = CreateLocationParam(**loc_data)
            created_loc = await location_service.create(db=db, obj=loc_param)
            created_locations.append(GetLocationDetail.model_validate(created_loc))
            location_ids.append(created_loc.id)

        # 更新demo的metadata，添加关联的文档和位置ID
        updated_metadata = created_demo.metadata_json or {}
        updated_metadata['document_ids'] = document_ids
        updated_metadata['location_ids'] = location_ids

        # 更新demo的tags，添加文档ID标记
        updated_tags = created_demo.tags or []
        for doc_id in document_ids:
            tag = f'doc_id_{doc_id}'
            if tag not in updated_tags:
                updated_tags.append(tag)

        # 更新demo的document_ids字段
        updated_document_ids = created_demo.document_ids or []
        updated_document_ids.extend(document_ids)

        # 执行更新操作
        update_param = AddDemoParam(
            username=created_demo.username,
            description=created_demo.description,
            metadata_json=updated_metadata,
            tags=updated_tags,
            document_ids=updated_document_ids,
            # 添加其他必要字段
            config_json=created_demo.config_json,
            settings_json=created_demo.settings_json,
            secret_key=created_demo.secret_key,
            api_token=created_demo.api_token,
            password_hash=created_demo.password_hash,
            phone=created_demo.phone,
            id_card=created_demo.id_card,
            score=created_demo.score,
            price=created_demo.price,
            birth_date=created_demo.birth_date,
            start_time=created_demo.start_time,
        )

        await demo_service.update(
            db=db,
            pk=created_demo.id,
            obj=update_param
        )

        # 重新获取完整的demo信息
        final_demo = await demo_service.getById(db=db, id=created_demo.id)

        return {
            'demo': GetDemoDetail.model_validate(final_demo),
            'documents': created_documents,
            'locations': created_locations
        }


demo_complex_service: DemoComplexService = DemoComplexService()