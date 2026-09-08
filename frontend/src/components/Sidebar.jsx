import { Box, Drawer, List, ListItemButton, ListItemIcon, ListItemText, Typography, Avatar, Divider } from "@mui/material";
import Inventory2Icon from "@mui/icons-material/Inventory2";
import DashboardIcon from "@mui/icons-material/Dashboard";
import BarChartIcon from "@mui/icons-material/BarChart";
import PersonIcon from "@mui/icons-material/Person";
import LogoutIcon from "@mui/icons-material/Logout";
import { NavLink, useNavigate } from "react-router-dom";

const DRAWER_WIDTH = 250;

const navItems = [
  { label: "Dashboard", icon: <DashboardIcon />, path: "/" },
  { label: "Reports", icon: <BarChartIcon />, path: "/reports/date-wise" },
];

export default function Sidebar() {
  const navigate = useNavigate();

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: DRAWER_WIDTH,
        flexShrink: 0,
        [`& .MuiDrawer-paper`]: {
          width: DRAWER_WIDTH,
          boxSizing: "border-box",
          bgcolor: "primary.main",
          color: "#fff",
        },
      }}
    >
      <Box sx={{ display: "flex", alignItems: "center", gap: 1.5, px: 2.5, py: 3 }}>
        <Inventory2Icon fontSize="large" />
        <Box>
          <Typography variant="subtitle1" fontWeight={700} lineHeight={1.1}>
            SKU Counter
          </Typography>
          <Typography variant="caption" sx={{ opacity: 0.75 }}>
            Vision Based Counting
          </Typography>
        </Box>
      </Box>

      <List sx={{ flexGrow: 1 }}>
        {navItems.map((item) => (
          <ListItemButton
            key={item.label}
            component={NavLink}
            to={item.path}
            sx={{
              mx: 1.5,
              my: 0.5,
              borderRadius: 2,
              "&.active": { bgcolor: "rgba(255,255,255,0.15)" },
              "&:hover": { bgcolor: "rgba(255,255,255,0.1)" },
            }}
          >
            <ListItemIcon sx={{ color: "#fff", minWidth: 36 }}>{item.icon}</ListItemIcon>
            <ListItemText primary={item.label} />
          </ListItemButton>
        ))}
      </List>

      <Divider sx={{ borderColor: "rgba(255,255,255,0.15)" }} />

      <Box sx={{ display: "flex", alignItems: "center", gap: 1.5, px: 2.5, py: 2 }}>
        <Avatar sx={{ bgcolor: "rgba(255,255,255,0.2)" }}>
          <PersonIcon />
        </Avatar>
        <Box sx={{ flexGrow: 1 }}>
          <Typography variant="body2" fontWeight={600}>
            Admin User
          </Typography>
          <Typography variant="caption" sx={{ opacity: 0.75 }}>
            Administrator
          </Typography>
        </Box>
      </Box>
      <ListItemButton onClick={() => navigate("/")} sx={{ mx: 1.5, mb: 2, borderRadius: 2 }}>
        <ListItemIcon sx={{ color: "#fff", minWidth: 36 }}>
          <LogoutIcon />
        </ListItemIcon>
        <ListItemText primary="Logout" />
      </ListItemButton>
    </Drawer>
  );
}

export { DRAWER_WIDTH };
