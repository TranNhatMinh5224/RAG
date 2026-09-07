import sys
import os
from pathlib import Path

# Đảm bảo UTF-8 cho Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from alembic.config import Config
from alembic import command

# Đảm bảo import được các module trong src/backend
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

from core.config import settings
from core.logger import get_logger

logger = get_logger("alembic.migration")


def get_alembic_config() -> Config:
    """Khởi tạo đối tượng cấu hình Alembic đồng bộ với settings hệ thống."""
    ini_path = backend_dir / "alembic.ini"
    if not ini_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file cấu hình {ini_path}")

    alembic_cfg = Config(str(ini_path))
    alembic_cfg.set_main_option("script_location", str(backend_dir / "alembic"))

    if settings.DATABASE_URL:
        alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

    return alembic_cfg


def make_migration(message: str):
    """
    Tự động quét cấu trúc Models trong code Python và sinh file migration mới:
    Tương đương: alembic revision --autogenerate -m "<message>"
    """
    if not message:
        print("❌ Vui lòng nhập mô tả cho migration! Ví dụ: python src/backend/migrate.py make 'add_user_bio'")
        sys.exit(1)

    cfg = get_alembic_config()
    print(f"🔍 Đang tự động quét Models và sinh file migration: '{message}'...")
    logger.info(f"Bắt đầu autogenerate migration: {message}")

    command.revision(cfg, message=message, autogenerate=True)

    print(f"✅ Đã tạo file migration thành công trong thư mục src/backend/alembic/versions/")
    logger.info(f"Đã tạo migration: {message}")


def upgrade_db():
    """Áp dụng toàn bộ migration mới nhất vào Database (alembic upgrade head)."""
    cfg = get_alembic_config()
    print("🚀 Đang thực thi Alembic Migration vào CSDL (command.upgrade)...")
    logger.info("Bắt đầu thực thi upgrade head")

    command.upgrade(cfg, "head")

    print("🎉 Hoàn tất Migration thành công! Tất cả các bảng CSDL đã đồng bộ.")
    logger.info("Hoàn tất upgrade head thành công")


def rollback_db():
    """Hạ phiên bản / Hoàn tác migration gần nhất (alembic downgrade -1)."""
    cfg = get_alembic_config()
    print("⚠️ Đang hoàn tác migration gần nhất (command.downgrade -1)...")
    logger.info("Bắt đầu downgrade -1")

    command.downgrade(cfg, "-1")

    print("✅ Đã hoàn tác migration gần nhất thành công!")
    logger.info("Hoàn tất downgrade -1")


def show_current():
    """Hiển thị revision hiện tại của Database."""
    cfg = get_alembic_config()
    print("📌 Trạng thái phiên bản Migration hiện tại:")
    command.current(cfg)


if __name__ == "__main__":
    args = sys.argv[1:]

    try:
        if not args or args[0] in ("upgrade", "up"):
            upgrade_db()
        elif args[0] in ("make", "create", "generate"):
            msg = args[1] if len(args) > 1 else "auto_migration"
            make_migration(msg)
        elif args[0] in ("rollback", "down", "downgrade"):
            rollback_db()
        elif args[0] in ("current", "status"):
            show_current()
        else:
            print("Cách sử dụng lệnh migrate:")
            print("  python src/backend/migrate.py make \"mo_ta\"   -> Tự động sinh file migration từ Model")
            print("  python src/backend/migrate.py                -> Chạy và cập nhật CSDL (upgrade head)")
            print("  python src/backend/migrate.py rollback       -> Hoàn tác thay đổi gần nhất")
            print("  python src/backend/migrate.py current        -> Xem phiên bản migration hiện tại")
    except Exception as e:
        print(f"❌ Lỗi khi xử lý migration: {e}")
        sys.exit(1)
