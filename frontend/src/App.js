import { BrowserRouter, Routes, Route } from "react-router-dom";
import "@fontsource/outfit/400.css";
import "@fontsource/outfit/500.css";
import "@fontsource/outfit/600.css";
import "@fontsource/outfit/700.css";
import "@fontsource/nunito/400.css";
import "@fontsource/nunito/500.css";
import "@fontsource/nunito/600.css";
import "@fontsource/nunito/700.css";
import "@/App.css";
import { Toaster } from "@/components/ui/sonner";
import LandingPage from "@/pages/LandingPage";
import ChatPage from "@/pages/ChatPage";

function App() {
  return (
    <div className="App min-h-screen bg-[#F2F2F7]">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/chat/:sessionId" element={<ChatPage />} />
        </Routes>
      </BrowserRouter>
      <Toaster position="top-center" richColors />
    </div>
  );
}

export default App;
