import asyncio
import os
import sys
import argparse

sys.path.insert(0, os.path.abspath("src/backend"))
from core.database import AsyncSessionLocal
from models import Document
from services.vector_store import VectorStoreManager
from sqlalchemy import select

async def reindex(document_id: int = None):
    print("=" * 60)
    print("BẮT ĐẦU RE-INDEXING TÀI LIỆU VỚI PIPELINE CẤU TRÚC MỚI")
    print("=" * 60)
    
    vsm = VectorStoreManager()
    
    async with AsyncSessionLocal() as session:
        if document_id:
            stmt = select(Document).where(Document.id == document_id)
        else:
            stmt = select(Document).order_by(Document.id.asc())
            
        result = await session.execute(stmt)
        docs = result.scalars().all()
        
        if not docs:
            print("Không tìm thấy tài liệu nào cần re-index.")
            return
            
        print(f"Tìm thấy {len(docs)} tài liệu cần xử lý lại:")
        for d in docs:
            print(f" - [ID {d.id}] {d.filename} ({d.file_path})")
            
        for d in docs:
            print(f"\n>>> Đang xử lý tài liệu ID: {d.id} ({d.filename})...")
            if not os.path.exists(d.file_path):
                print(f" Tệp không tồn tại trên ổ đĩa: {d.file_path}, bỏ qua.")
                continue
                
            try:
                # 1. Xóa toàn bộ vector cũ khỏi Qdrant
                await vsm.delete_document(d.id)
                
                # 2. Chạy lại Ingestion với Pipeline Structure-Aware mới
                await vsm.ingest_document_async(
                    file_path=d.file_path,
                    user_id=d.user_id,
                    document_id=d.id,
                    original_filename=d.filename
                )
                
                d.status = "READY"
                d.error_message = None
                await session.commit()
                print(f" Hoàn tất re-index thành công cho: {d.filename}")
            except Exception as e:
                print(f" Lỗi khi re-index tài liệu {d.id}: {e}")
                d.status = "FAILED"
                d.error_message = str(e)
                await session.commit()
                
    print("\n" + "=" * 60)
    print("ĐÃ HOÀN TẤT QUÁ TRÌNH RE-INDEXING TOÀN BỘ HỆ THỐNG!")
    print("=" * 60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--doc_id", type=int, default=None, help="ID tài liệu cụ thể cần re-index")
    args = parser.parse_args()
    
    asyncio.run(reindex(args.doc_id))
