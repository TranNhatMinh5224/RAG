import asyncio
import os
import sys
import time
import json
import csv
from typing import List, Dict, Any

# Ensure proper path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, BACKEND_DIR)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

from core.database import AsyncSessionLocal
from models import Document
from sqlalchemy import select
from api.dependencies import get_rag_chain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from core.config import settings

# 50 CÂU HỎI BENCHMARK CHUẨN ĐƯỢC THIẾT KẾ DỰA TRÊN TÀI LIỆU
BENCHMARK_QUESTIONS: List[Dict[str, Any]] = [
    # --- CẤP ĐỘ 1: Nhận biết & Thông tin trực diện (15 câu) ---
    {
        "id": 1,
        "level": "Level 1 (Factual)",
        "question": "Tên chính xác của đề tài nghiên cứu được đề xuất trong tài liệu là gì?",
        "ground_truth": "Ứng dụng Deep Learning trong học biểu diễn cho dữ liệu y tế phân mảnh.",
        "trap": False
    },
    {
        "id": 2,
        "level": "Level 1 (Factual)",
        "question": "Báo cáo đề cập đến những hệ thống phần mềm quản lý y tế phổ biến nào trong bệnh viện?",
        "ground_truth": "HIS (Hospital Information System), LIS (Laboratory Information System), RIS/PACS, EMR (Electronic Medical Record) và hệ thống theo dõi bệnh nhân/thiết bị y tế.",
        "trap": False
    },
    {
        "id": 3,
        "level": "Level 1 (Factual)",
        "question": "Hệ thống HIS viết tắt của cụm từ tiếng Anh nào và quản lý những loại thông tin gì?",
        "ground_truth": "Hospital Information System. Quản lý thông tin bệnh nhân, lượt khám, nhập viện, khoa/phòng điều trị, dịch vụ, viện phí, đơn thuốc.",
        "trap": False
    },
    {
        "id": 4,
        "level": "Level 1 (Factual)",
        "question": "Hệ thống LIS viết tắt của cụm từ gì và lưu trữ những kết quả xét nghiệm nào?",
        "ground_truth": "Laboratory Information System. Lưu kết quả xét nghiệm máu, nước tiểu, đường huyết, công thức máu, chức năng gan, thận, sinh hóa, vi sinh...",
        "trap": False
    },
    {
        "id": 5,
        "level": "Level 1 (Factual)",
        "question": "Hệ thống RIS/PACS quản lý loại dữ liệu y khoa nào?",
        "ground_truth": "Quản lý chẩn đoán hình ảnh: ảnh X-quang, CT, MRI, siêu âm và kết quả đọc ảnh của bác sĩ.",
        "trap": False
    },
    {
        "id": 6,
        "level": "Level 1 (Factual)",
        "question": "Bệnh án điện tử EMR lưu lại những quá trình điều trị nào của người bệnh?",
        "ground_truth": "Lưu quá trình điều trị, tiền sử bệnh, chẩn đoán, thuốc sử dụng, chỉ định điều trị, thủ thuật, diễn biến bệnh và kết quả điều trị.",
        "trap": False
    },
    {
        "id": 7,
        "level": "Level 1 (Factual)",
        "question": "Các thiết bị y tế theo dõi bệnh nhân thường ghi nhận liên tục những dấu hiệu sinh tồn nào?",
        "ground_truth": "Nhịp tim, huyết áp, SpO2, nhịp thở, nhiệt độ cơ thể.",
        "trap": False
    },
    {
        "id": 8,
        "level": "Level 1 (Factual)",
        "question": "Trước khi số hóa, phần lớn thông tin khám chữa bệnh được lưu trữ trên những phương tiện gì?",
        "ground_truth": "Ghi trên giấy, sổ khám bệnh, phiếu xét nghiệm và phim chụp.",
        "trap": False
    },
    {
        "id": 9,
        "level": "Level 1 (Factual)",
        "question": "Tài liệu chia dữ liệu y tế thành mấy dạng chính? Kể tên các dạng đó.",
        "ground_truth": "4 dạng: Dữ liệu dạng bảng, Dữ liệu chuỗi thời gian, Dữ liệu văn bản, Dữ liệu hình ảnh.",
        "trap": False
    },
    {
        "id": 10,
        "level": "Level 1 (Factual)",
        "question": "Tuổi, giới tính, kết quả xét nghiệm, thuốc thuộc dạng dữ liệu y tế nào?",
        "ground_truth": "Dữ liệu dạng bảng (tabular data).",
        "trap": False
    },
    {
        "id": 11,
        "level": "Level 1 (Factual)",
        "question": "Ghi chú lâm sàng và kết luận của bác sĩ thuộc dạng dữ liệu nào?",
        "ground_truth": "Dữ liệu văn bản (text data).",
        "trap": False
    },
    {
        "id": 12,
        "level": "Level 1 (Factual)",
        "question": "Hình ảnh X-quang, CT, MRI, siêu âm được xếp vào dạng dữ liệu gì?",
        "ground_truth": "Dữ liệu hình ảnh (image data).",
        "trap": False
    },
    {
        "id": 13,
        "level": "Level 1 (Factual)",
        "question": "Nhóm nghiên cứu lựa chọn bộ dữ liệu nào làm dữ liệu thực nghiệm?",
        "ground_truth": "Bộ dữ liệu MIMIC-IV.",
        "trap": False
    },
    {
        "id": 14,
        "level": "Level 1 (Factual)",
        "question": "Trong bộ dữ liệu MIMIC-IV, nhóm tác giả tập trung vào dữ liệu bệnh nhân tại khu vực nào?",
        "ground_truth": "Khu vực ICU (Intensive Care Unit - Đơn vị chăm sóc tích cực).",
        "trap": False
    },
    {
        "id": 15,
        "level": "Level 1 (Factual)",
        "question": "Cụm từ viết tắt ICU có nghĩa là gì trong tiếng Anh và tiếng Việt?",
        "ground_truth": "Intensive Care Unit – Đơn vị chăm sóc tích cực.",
        "trap": False
    },

    # --- CẤP ĐỘ 2: Thông hiểu & Khái niệm kỹ thuật (15 câu) ---
    {
        "id": 16,
        "level": "Level 2 (Conceptual)",
        "question": "Thế nào là hiện tượng 'dữ liệu y tế bị phân mảnh'?",
        "ground_truth": "Dữ liệu liên quan đến cùng một bệnh nhân không được lưu tập trung tại một nơi mà bị chia rẽ, rải rác ở nhiều hệ thống phần mềm (HIS, LIS, PACS, EMR) và thời điểm khác nhau.",
        "trap": False
    },
    {
        "id": 17,
        "level": "Level 2 (Conceptual)",
        "question": "Sự phân mảnh dữ liệu y tế có thể xảy ra theo những chiều nào?",
        "ground_truth": "Phân mảnh giữa nhiều hệ thống phần mềm trong cùng bệnh viện, phân mảnh theo thời gian (nhiều lần khám) và phân mảnh giữa nhiều cơ sở y tế khác nhau.",
        "trap": False
    },
    {
        "id": 18,
        "level": "Level 2 (Conceptual)",
        "question": "Ba dạng không đồng nhất chính ảnh hưởng trực tiếp đến khả năng khai thác AI trong y tế là gì?",
        "ground_truth": "Khác cấu trúc dữ liệu (Schema heterogeneity), Thiếu dữ liệu (Missingness), và Khác phân phối (Distribution shift / Domain shift).",
        "trap": False
    },
    {
        "id": 19,
        "level": "Level 2 (Conceptual)",
        "question": "Hiện tượng khác cấu trúc (Schema Heterogeneity) là gì? Cho ví dụ từ tài liệu.",
        "ground_truth": "Xảy ra khi các bộ dữ liệu không có cùng tập thuộc tính (khác số chiều và ý nghĩa). Ví dụ: Bệnh viện này có SpO2 và nhiệt độ nhưng không có CRP; bệnh viện khác có CRP nhưng không có đầy đủ dấu hiệu sinh tồn.",
        "trap": False
    },
    {
        "id": 20,
        "level": "Level 2 (Conceptual)",
        "question": "Hiện tượng thiếu dữ liệu (Missingness) trong lâm sàng thường bắt nguồn từ những nguyên nhân nào?",
        "ground_truth": "Do bác sĩ đánh giá không cần thiết chỉ định xét nghiệm, do cảm biến bị gián đoạn, hoặc do hệ thống không lưu trường dữ liệu đó.",
        "trap": False
    },
    {
        "id": 21,
        "level": "Level 2 (Conceptual)",
        "question": "Tại sao tài liệu lại nhấn mạnh rằng 'không có giá trị' (missing) đôi khi mang thông tin khác với giá trị bằng 0?",
        "ground_truth": "Vì trong lâm sàng, việc không làm xét nghiệm phản ánh tình trạng bệnh nhân không có triệu chứng nghi ngờ hoặc quyết định của bác sĩ, chứ không đồng nghĩa với chỉ số bằng 0. Cần được mô hình xử lý có chủ đích.",
        "trap": False
    },
    {
        "id": 22,
        "level": "Level 2 (Conceptual)",
        "question": "Hiện tượng khác phân phối (Distribution Shift / Domain Shift) giữa các bệnh viện được giải thích như thế nào?",
        "ground_truth": "Xảy ra khi đặc điểm bệnh nhân, mô hình bệnh tật, thiết bị đo hoặc quy trình chuyên môn khác nhau giữa các cơ sở.",
        "trap": False
    },
    {
        "id": 23,
        "level": "Level 2 (Conceptual)",
        "question": "Vì sao hai bệnh viện có cùng một tên feature nhưng vẫn xảy ra hiện tượng Domain Shift?",
        "ground_truth": "Vì phân phối giá trị của feature và mối liên hệ giữa feature với outcome (kết quả lâm sàng) có thể khác nhau do sự khác biệt về dân số bệnh nhân, độ tuổi hoặc quy trình đo.",
        "trap": False
    },
    {
        "id": 24,
        "level": "Level 2 (Conceptual)",
        "question": "Một bệnh nhân đến khám và điều trị tại bệnh viện có thể tạo ra dữ liệu từ lúc tiếp nhận đến khi xuất viện ra sao?",
        "ground_truth": "Ghi nhận thông tin cá nhân, chẩn đoán ban đầu, xét nghiệm, thuốc, nhịp tim, huyết áp liên tục, hình ảnh X-quang/CT và ghi chú lâm sàng từ lúc tiếp nhận tới khi xuất viện.",
        "trap": False
    },
    {
        "id": 25,
        "level": "Level 2 (Conceptual)",
        "question": "Tại sao nói dữ liệu y tế là nguồn thông tin giá trị cho AI nhưng cũng làm việc khai thác trở nên phức tạp hơn?",
        "ground_truth": "Giá trị vì dữ liệu đa chiều, phong phú phản ánh toàn diện sức khỏe; phức tạp vì không đồng nhất, đa định dạng (bảng, ảnh, văn bản, chuỗi thời gian) và bị chia nhỏ ở nhiều nơi.",
        "trap": False
    },
    {
        "id": 26,
        "level": "Level 2 (Conceptual)",
        "question": "Để có đầy đủ thông tin về một bệnh nhân điều trị, vì sao phải lấy dữ liệu từ nhiều hệ thống khác nhau?",
        "ground_truth": "Vì mỗi hệ thống chỉ phụ trách một mảng nghiệp vụ riêng: HIS quản lý hành chính/viện phí, LIS quản lý xét nghiệm, PACS quản lý hình ảnh, EMR quản lý bệnh án, Monitor theo dõi sinh hiệu.",
        "trap": False
    },
    {
        "id": 27,
        "level": "Level 2 (Conceptual)",
        "question": "Mục tiêu cốt lõi của đề tài học biểu diễn cho dữ liệu y tế phân mảnh là gì?",
        "ground_truth": "Xây dựng mô hình có khả năng khai thác thông tin từ nhiều nguồn dữ liệu y tế khác nhau, học được những đặc trưng chung giữa các nguồn nhưng vẫn giữ được thông tin riêng có giá trị của từng nguồn.",
        "trap": False
    },
    {
        "id": 28,
        "level": "Level 2 (Conceptual)",
        "question": "Khái niệm 'học đặc trưng chung' và 'bảo toàn thông tin riêng' trong đề tài mang ý nghĩa gì?",
        "ground_truth": "Học đặc trưng chung giúp mô hình có khả năng tổng quát hóa trên nhiều cơ sở y tế; bảo toàn thông tin riêng giúp không bỏ phí các thuộc tính giá trị độc thù mà chỉ một số bệnh viện có.",
        "trap": False
    },
    {
        "id": 29,
        "level": "Level 2 (Conceptual)",
        "question": "Tại sao MIMIC-IV được đánh giá là nguồn dữ liệu rất phù hợp để nghiên cứu bài toán phân mảnh?",
        "ground_truth": "Vì dữ liệu của một bệnh nhân được tạo ra từ nhiều loại thông tin khác nhau (chẩn đoán, xét nghiệm, thuốc, thủ thuật, sinh hiệu) trong suốt quá trình điều trị tại ICU.",
        "trap": False
    },
    {
        "id": 30,
        "level": "Level 2 (Conceptual)",
        "question": "Bộ dữ liệu MIMIC-IV tại ICU bao gồm những nhóm thông tin đa dạng nào của bệnh nhân?",
        "ground_truth": "Thông tin bệnh nhân, chẩn đoán, xét nghiệm, thuốc, thủ thuật và các dấu hiệu sinh tồn như nhịp tim, huyết áp, SpO2.",
        "trap": False
    },

    # --- CẤP ĐỘ 3: Suy luận & Phân tích hệ thống (12 câu) ---
    {
        "id": 31,
        "level": "Level 3 (Reasoning)",
        "question": "Vì sao các mô hình AI thông thường/truyền thống lại gặp bế tắc khi áp dụng trên dữ liệu y tế đa nguồn?",
        "ground_truth": "Vì chúng yêu cầu một cấu trúc/schema cố định (học với feature nào thì khi dự đoán phải có đúng các feature đó). Khi sang bệnh viện mới bị lệch feature hoặc thiếu trường thì mô hình không thể chạy được.",
        "trap": False
    },
    {
        "id": 32,
        "level": "Level 3 (Reasoning)",
        "question": "Hãy phân tích ví dụ so sánh giữa Bệnh viện A và Bệnh viện B trong tài liệu để làm rõ hạn chế của mô hình có schema cố định.",
        "ground_truth": "Bệnh viện A có: Tuổi - Giới tính - Huyết áp - Đường huyết - Cholesterol. Bệnh viện B chỉ có: Tuổi - Giới tính - Huyết áp - HbA1c. Thiếu Cholesterol và thay bằng HbA1c khiến mô hình từ A không áp dụng trực tiếp cho B.",
        "trap": False
    },
    {
        "id": 33,
        "level": "Level 3 (Reasoning)",
        "question": "Nếu giải quyết bài toán khác cấu trúc bằng cách 'chỉ giữ lại những thông tin giống nhau giữa các bệnh viện', hệ quả tiêu cực là gì?",
        "ground_truth": "Sẽ phải bỏ đi rất nhiều dữ liệu và đặc trưng riêng có giá trị của từng bệnh viện (ví dụ bỏ mất xét nghiệm chuyên sâu), làm giảm sức mạnh của mô hình.",
        "trap": False
    },
    {
        "id": 34,
        "level": "Level 3 (Reasoning)",
        "question": "Tại sao các bệnh viện tuyến nhỏ hoặc cơ sở ít dữ liệu lại gặp khó khăn nếu cố gắng tự huấn luyện mô hình AI riêng lẻ?",
        "ground_truth": "Do lượng dữ liệu quá nhỏ, mô hình dễ bị học chưa tốt (underfitting) hoặc bị quá khớp (overfitting), không đảm bảo độ tin cậy.",
        "trap": False
    },
    {
        "id": 35,
        "level": "Level 3 (Reasoning)",
        "question": "Vì sao việc giải quyết bài toán phân mảnh dữ liệu y tế không đơn thuần là 'chọn một thuật toán dự đoán tốt hơn'?",
        "ground_truth": "Vì vấn đề gốc rễ nằm ở biểu diễn dữ liệu và sự không đồng nhất (schema, missingness, domain shift). Cần một phương pháp học biểu diễn (representation learning) linh hoạt chứ không chỉ là thuật toán phân loại.",
        "trap": False
    },
    {
        "id": 36,
        "level": "Level 3 (Reasoning)",
        "question": "Bằng cách nào mà Deep Learning được kỳ vọng giải quyết được bài toán học biểu diễn từ các nguồn dữ liệu phân mảnh?",
        "ground_truth": "Bằng cách học biểu diễn ẩn (representation learning) để trích xuất không gian đặc trưng chung từ các dạng dữ liệu đa thể thức (multimodal), đồng thời ánh xạ các thuộc tính riêng rẽ.",
        "trap": False
    },
    {
        "id": 37,
        "level": "Level 3 (Reasoning)",
        "question": "Phân tích nguyên nhân khiến một mô hình AI có độ chính xác rất cao tại nơi huấn luyện nhưng lại suy giảm nghiêm trọng khi triển khai ở bệnh viện mới?",
        "ground_truth": "Do Domain Shift: khác biệt về phân phối bệnh nhân, độ tuổi, bệnh nền, thiết bị đo và quy trình lâm sàng giữa bệnh viện huấn luyện và môi trường mới.",
        "trap": False
    },
    {
        "id": 38,
        "level": "Level 3 (Reasoning)",
        "question": "Sự khác biệt về thiết bị đo và quy trình chuyên môn giữa các cơ sở y tế ảnh hưởng thế nào đến tính tin cậy của mô hình AI?",
        "ground_truth": "Làm thay đổi phân phối giá trị và mối quan hệ giữa biến số đầu vào với kết cục điều trị, khiến mô hình đưa ra suy luận sai lệch nếu không được chuẩn hóa thích nghi miền.",
        "trap": False
    },
    {
        "id": 39,
        "level": "Level 3 (Reasoning)",
        "question": "Tại sao dữ liệu tại khoa hồi sức tích cực (ICU) lại được coi là bài toán đại diện điển hình nhất cho sự phân mảnh dữ liệu y tế?",
        "ground_truth": "Vì bệnh nhân ICU có diễn biến bệnh phức tạp nhất, được theo dõi sinh hiệu liên tục, thực hiện vô số xét nghiệm khẩn cấp, thuốc và thủ thuật từ nhiều hệ thống trong thời gian ngắn.",
        "trap": False
    },
    {
        "id": 40,
        "level": "Level 3 (Reasoning)",
        "question": "Hãy tổng hợp chuỗi logic hình thành nên bài toán nghiên cứu từ khâu số hóa đến đề xuất đề tài.",
        "ground_truth": "Số hóa y tế -> Dữ liệu phát sinh lớn & đa dạng -> Dữ liệu bị lưu rải rác (phân mảnh) -> 3 dạng không đồng nhất (schema, missing, domain shift) -> AI truyền thống thất bại -> Đề xuất Deep Learning học biểu diễn dữ liệu phân mảnh.",
        "trap": False
    },
    {
        "id": 41,
        "level": "Level 3 (Reasoning)",
        "question": "Mối liên hệ giữa việc thiếu hụt dữ liệu (Missingness) và sự thiên lệch nếu thay thế đơn giản bằng số 0?",
        "ground_truth": "Nếu gán bừa bằng 0 sẽ làm sai lệch bản chất lâm sàng, vì missing mang thông tin về quyết định không chỉ định của bác sĩ chứ không phải chỉ số xét nghiệm bằng 0.",
        "trap": False
    },
    {
        "id": 42,
        "level": "Level 3 (Reasoning)",
        "question": "Ý nghĩa thực tiễn của nghiên cứu này đối với quá trình phát triển các hệ thống hỗ trợ ra quyết định lâm sàng (CDSS)?",
        "ground_truth": "Khắc phục tình trạng suy giảm hiệu năng khi nhân rộng mô hình AI sang các bệnh viện mới, giúp ứng dụng AI trong y tế bền vững, chính xác và khai thác được dữ liệu đa nguồn.",
        "trap": False
    },

    # --- CẤP ĐỘ 4: Kiểm thử bẫy & Chống Ảo giác (8 câu) ---
    {
        "id": 43,
        "level": "Level 4 (Trap/Hallucination)",
        "question": "Độ chính xác (Accuracy) hoặc chỉ số AUC-ROC của mô hình đề xuất đạt được là bao nhiêu phần trăm?",
        "ground_truth": "Tài liệu này là báo cáo khảo sát bối cảnh và đề xuất bài toán nghiên cứu, KHÔNG trình bày kết quả thực nghiệm hay số liệu Accuracy/AUC-ROC cụ thể nào.",
        "trap": True
    },
    {
        "id": 44,
        "level": "Level 4 (Trap/Hallucination)",
        "question": "Pipeline chi tiết mà tác giả đề xuất gồm những bước thuật toán cụ thể nào?",
        "ground_truth": "Tài liệu chỉ ghi chú 'Pipeline đề xuất: (đợi em minh xoăn)' và CHƯA cung cấp các bước chi tiết của pipeline.",
        "trap": True
    },
    {
        "id": 45,
        "level": "Level 4 (Trap/Hallucination)",
        "question": "Nhóm nghiên cứu đã so sánh mô hình của mình với mô hình XGBoost và Random Forest chưa? Kết quả ra sao?",
        "ground_truth": "Tài liệu KHÔNG đề cập đến việc so sánh với XGBoost hay Random Forest.",
        "trap": True
    },
    {
        "id": 46,
        "level": "Level 4 (Trap/Hallucination)",
        "question": "Tài liệu có đề cập đến việc bảo mật dữ liệu y tế theo chuẩn HIPAA hay GDPR không?",
        "ground_truth": "Tài liệu KHÔNG đề cập đến chuẩn bảo mật HIPAA hay GDPR.",
        "trap": True
    },
    {
        "id": 47,
        "level": "Level 4 (Trap/Hallucination)",
        "question": "Chi phí đầu tư hoặc giá bản quyền của hệ thống phần mềm HIS/LIS được nhắc đến là bao nhiêu tiền?",
        "ground_truth": "Tài liệu KHÔNG đề cập đến bất kỳ chi phí đầu tư hay giá tiền mua phần mềm nào.",
        "trap": True
    },
    {
        "id": 48,
        "level": "Level 4 (Trap/Hallucination)",
        "question": "Nhóm tác giả của báo cáo gồm những ai và thuộc trường đại học nào?",
        "ground_truth": "Tài liệu KHÔNG ghi rõ danh sách thành viên nhóm tác giả hay tên trường đại học.",
        "trap": True
    },
    {
        "id": 49,
        "level": "Level 4 (Trap/Hallucination)",
        "question": "Mô hình Deep Learning trong báo cáo sử dụng cấu trúc mạng Transformer, LSTM hay CNN?",
        "ground_truth": "Tài liệu chỉ nói chung về việc ứng dụng Deep Learning trong học biểu diễn, CHƯA chỉ định cụ thể kiến trúc mạng là Transformer, LSTM hay CNN.",
        "trap": True
    },
    {
        "id": 50,
        "level": "Level 4 (Trap/Hallucination)",
        "question": "Tổng số lượng bệnh nhân và số ca tử vong trong tập dữ liệu MIMIC-IV được dùng trong bài là bao nhiêu người?",
        "ground_truth": "Tài liệu KHÔNG đưa ra con số cụ thể về số lượng bệnh nhân hay số ca tử vong trong tập MIMIC-IV.",
        "trap": True
    },
]

JUDGE_PROMPT_TEMPLATE = PromptTemplate(
    input_variables=["question", "ground_truth", "model_answer", "is_trap"],
    template="""Bạn là một Giám khảo AI chuyên gia đánh giá hệ thống RAG (Retrieval-Augmented Generation).
Nhiệm vụ của bạn là chấm điểm câu trả lời của hệ thống RAG dựa trên Câu hỏi và Chuẩn đáp án (Ground Truth).

THÔNG TIN ĐÁNH GIÁ:
- Câu hỏi: {question}
- Chuẩn đáp án / Kỳ vọng: {ground_truth}
- Câu trả lời của RAG: {model_answer}
- Đây có phải câu hỏi bẫy (thông tin không có trong tài liệu) không: {is_trap}

TIÊU CHÍ CHẤM ĐIỂM:
1. Đối với câu hỏi thông thường:
   - PASS (Đúng - 8 đến 10 điểm): Trả lời đúng trọng tâm, chứa các ý chính của chuẩn đáp án, không sai lệch, có trích dẫn nguồn.
   - PARTIAL (Đúng một phần - 5 đến 7 điểm): Trả lời được một số ý nhưng còn thiếu sót hoặc chưa thật đầy đủ.
   - FAIL (Sai - 0 đến 4 điểm): Trả lời sai bản chất, lạc đề, hoặc không tìm thấy thông tin dù trong tài liệu có.
2. Đối với câu hỏi bẫy (is_trap = True):
   - PASS (Đúng - 10 điểm): Hệ thống TRUNG THỰC trả lời là tài liệu không đề cập/không có thông tin này (KHÔNG BỊA ĐẶT / ZERO HALLUCINATION).
   - FAIL (Sai - 0 điểm): Hệ thống tự ý bịa đặt số liệu, tên kiến trúc hoặc thông tin sai sự thật (HALLUCINATION).

ĐỊNH DẠNG TRẢ VỀ (BẮT BUỘC LÀ JSON DUY NHẤT, KHÔNG THÊM BẤT KỲ VĂN BẢN NÀO KHÁC):
{{
  "verdict": "PASS" hoặc "PARTIAL" hoặc "FAIL",
  "score": <điểm số từ 0 đến 10>,
  "reason": "<lý giải ngắn gọn 1-2 câu vì sao cho điểm này>"
}}
"""
)

async def run_benchmark(limit: int = 50):
    print("=" * 70)
    print(f"BẮT ĐẦU CHẠY BENCHMARK RAG TRÊN {limit} CÂU HỎI (ĐA CẤP ĐỘ)")
    print("=" * 70)

    # 1. Tìm tài liệu trong CSDL
    async with AsyncSessionLocal() as session:
        stmt = select(Document).order_by(Document.id.desc())
        docs = (await session.execute(stmt)).scalars().all()
        
        target_doc = None
        for d in docs:
            if "Bao_cao_Boi_canh" in d.filename or "Y_te" in d.filename:
                target_doc = d
                break
        if not target_doc and docs:
            target_doc = docs[0]

        if not target_doc:
            print("LỖI: Không tìm thấy tài liệu nào trong hệ thống! Vui lòng nạp tài liệu trước.")
            return

        print(f"Đang kiểm thử trên tài liệu: ID={target_doc.id} - {target_doc.filename}")
        doc_id = target_doc.id
        user_id = target_doc.user_id

    # 2. Khởi tạo RAGChain và Judge LLM (Ollama Local)
    rag_chain = get_rag_chain()
    from langchain_ollama import ChatOllama
    print(f"⚖️ Khởi tạo Giám khảo AI (LLM Judge) bằng Ollama: '{settings.OLLAMA_MODEL}'...")
    judge_llm = ChatOllama(
        model=settings.OLLAMA_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=0.0
    )

    results = []
    questions_to_run = BENCHMARK_QUESTIONS[:limit]

    print(f"\nTiến trình kiểm thử {len(questions_to_run)} câu hỏi:")
    print("-" * 70)

    pass_count = 0
    partial_count = 0
    fail_count = 0
    total_score = 0.0

    start_time_all = time.time()

    for idx, q_item in enumerate(questions_to_run, 1):
        q_id = q_item["id"]
        level = q_item["level"]
        question = q_item["question"]
        ground_truth = q_item["ground_truth"]
        is_trap = q_item["trap"]

        print(f"[{idx}/{len(questions_to_run)}] [{level}] Q: {question[:60]}...", end="", flush=True)

        t0 = time.time()
        try:
            # Chạy qua RAG Chain
            rag_answer = await rag_chain.answer_question_async(
                question=question,
                user_id=user_id,
                document_ids=[doc_id],
                chat_history="",
                conversation_id=9999,
                conversation_summary="",
            )
        except Exception as e:
            rag_answer = f"LỖI RAG: {e}"
        latency = round(time.time() - t0, 2)

        # Chạy Giám khảo LLM Judge
        try:
            judge_prompt = JUDGE_PROMPT_TEMPLATE.format(
                question=question,
                ground_truth=ground_truth,
                model_answer=rag_answer,
                is_trap=str(is_trap)
            )
            judge_res = await judge_llm.ainvoke(judge_prompt)
            raw_content = judge_res.content.strip()
            # Clean json
            if raw_content.startswith("```json"):
                raw_content = raw_content[7:]
            if raw_content.endswith("```"):
                raw_content = raw_content[:-3]
            eval_data = json.loads(raw_content.strip())
        except Exception as e:
            eval_data = {
                "verdict": "FAIL",
                "score": 0,
                "reason": f"Lỗi Giám khảo: {e}"
            }

        verdict = eval_data.get("verdict", "FAIL")
        score = float(eval_data.get("score", 0))
        reason = eval_data.get("reason", "")

        total_score += score
        if verdict == "PASS":
            pass_count += 1
            status_symbol = "✅ PASS"
        elif verdict == "PARTIAL":
            partial_count += 1
            status_symbol = "⚠️ PARTIAL"
        else:
            fail_count += 1
            status_symbol = "❌ FAIL"

        print(f" -> {status_symbol} ({score}/10) [{latency}s]")

        results.append({
            "id": q_id,
            "level": level,
            "question": question,
            "ground_truth": ground_truth,
            "is_trap": is_trap,
            "rag_answer": rag_answer,
            "latency_seconds": latency,
            "verdict": verdict,
            "score": score,
            "reason": reason
        })

    total_time = round(time.time() - start_time_all, 2)
    avg_score = round(total_score / len(questions_to_run), 2)
    pass_rate = round((pass_count / len(questions_to_run)) * 100, 1)

    print("\n" + "=" * 70)
    print("TỔNG KẾT KẾT QUẢ BENCHMARK")
    print("=" * 70)
    print(f"Tổng số câu hỏi: {len(questions_to_run)}")
    print(f"Thời gian thực thi: {total_time}s (Trung bình {round(total_time/len(questions_to_run), 2)}s/câu)")
    print(f"Đạt (PASS): {pass_count} ({pass_rate}%)")
    print(f"Đạt một phần (PARTIAL): {partial_count}")
    print(f"Không đạt (FAIL): {fail_count}")
    print(f"Điểm số trung bình: {avg_score} / 10.0")

    # Xuất ra CSV
    csv_file = "c:/Users/Minh/Desktop/My-Project/RAG/benchmark_results.csv"
    with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Level", "Question", "Ground Truth", "Is Trap", "RAG Answer", "Verdict", "Score", "Latency (s)", "Judge Reason"])
        for r in results:
            writer.writerow([
                r["id"], r["level"], r["question"], r["ground_truth"],
                r["is_trap"], r["rag_answer"], r["verdict"], r["score"],
                r["latency_seconds"], r["reason"]
            ])

    # Xuất ra JSON
    json_file = "c:/Users/Minh/Desktop/My-Project/RAG/benchmark_results.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "total_questions": len(questions_to_run),
                "total_time_seconds": total_time,
                "average_score": avg_score,
                "pass_rate_percent": pass_rate,
                "pass_count": pass_count,
                "partial_count": partial_count,
                "fail_count": fail_count
            },
            "details": results
        }, f, ensure_ascii=False, indent=2)

    print(f"\nĐã xuất báo cáo chi tiết ra:")
    print(f" - CSV: {csv_file}")
    print(f" - JSON: {json_file}")
    print("=" * 70)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=50, help="Số lượng câu hỏi muốn test")
    args = parser.parse_args()
    asyncio.run(run_benchmark(args.limit))
