import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import ChatView from "./components/ChatView";
import SettingsPanel from "./components/SettingsPanel";
import Toast from "./components/Toast";

export default function App() {
  return (
    <Router>
      <div className="flex h-screen w-screen overflow-hidden bg-[var(--bg-primary)]">
        <Sidebar />
        <main className="flex-1 flex flex-col min-w-0">
          <Routes>
            <Route path="/" element={<ChatView />} />
          </Routes>
        </main>
        <SettingsPanel />
        <Toast />
      </div>
    </Router>
  );
}