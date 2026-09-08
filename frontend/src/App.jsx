import { Box } from "@mui/material";
import { Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import DateWiseReport from "./pages/DateWiseReport";
import SkuWiseReport from "./pages/SkuWiseReport";

export default function App() {
  return (
    <Box sx={{ display: "flex", minHeight: "100vh", bgcolor: "background.default" }}>
      <Sidebar />
      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/reports/date-wise" element={<DateWiseReport />} />
          <Route path="/reports/sku-wise" element={<SkuWiseReport />} />
        </Routes>
      </Box>
    </Box>
  );
}
