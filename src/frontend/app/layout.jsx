import 'bootstrap/dist/css/bootstrap.min.css';
import '../src/index.css';
import 'react-toastify/dist/ReactToastify.css';
import { AuthProvider } from '../src/contexts/AuthContext';
import { ToastContainer } from 'react-toastify';

export const metadata = {
  title: 'NexusDoc AI • Enterprise Research Intelligence',
  description: 'Nền tảng trợ lý AI chuyên sâu bóc tách, đối chiếu và phân tích đa tài liệu nguồn',
};

export default function RootLayout({ children }) {
  return (
    <html lang="vi">
      <body>
        <AuthProvider>
          {children}
          <ToastContainer theme="dark" position="bottom-right" />
        </AuthProvider>
      </body>
    </html>
  );
}
