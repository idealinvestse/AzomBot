import {
  BrowserRouter as Router,
  Routes,
  Route,
  NavLink,
} from "react-router-dom";
import { LayoutDashboard, MessageCircle, FileText, Activity, Sliders, BarChart2 } from "lucide-react";
import ChatPage from "@/pages/ChatPage";
import { SettingsPage } from "@/pages/SettingsPage";
import LogsPage from "@/pages/LogsPage";
import StatusPage from "@/pages/StatusPage";
import CustomizePage from "@/pages/CustomizePage";
import StatsPage from "@/pages/StatsPage";

function Sidebar() {
  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `flex items-center px-4 py-2 rounded-md hover:bg-accent hover:text-accent-foreground transition-colors text-sm gap-2 ${
      isActive ? "bg-primary text-primary-foreground" : ""
    }`;
  return (
    <div className="h-screen w-56 border-r bg-background p-4 space-y-4">
      <h1 className="text-lg font-semibold">AZOM Dashboard</h1>
      <nav className="flex flex-col gap-1">
        <NavLink to="/" className={linkClass} end>
          <LayoutDashboard className="h-4 w-4" />Översikt
        </NavLink>
        <NavLink to="/chat" className={linkClass}>
          <MessageCircle className="h-4 w-4" />Chat
        </NavLink>
        <NavLink to="/logs" className={linkClass}>
          <FileText className="h-4 w-4" />Loggar
        </NavLink>
        <NavLink to="/status" className={linkClass}>
          <Activity className="h-4 w-4" />Status
        </NavLink>
        <NavLink to="/customize" className={linkClass}>
          <Sliders className="h-4 w-4" />Anpassa
        </NavLink>
        <NavLink to="/stats" className={linkClass}>
          <BarChart2 className="h-4 w-4" />Statistik
        </NavLink>
        <NavLink to="/settings" className={linkClass}>
          <Sliders className="h-4 w-4" />Inställningar
        </NavLink>
      </nav>
    </div>
  );
}

export default function App() {
  return (
    <Router>
      <div className="flex">
        <Sidebar />
        <div className="flex-1 min-h-screen bg-muted/20 p-6">
          <Routes>
            <Route path="/" element={<div>Välkommen till dashboarden!</div>} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/logs" element={<LogsPage />} />
            <Route path="/status" element={<StatusPage />} />
            <Route path="/customize" element={<CustomizePage />} />
            <Route path="/stats" element={<StatsPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}
