import { Box, Typography, Chip, Avatar, Button } from "@mui/material";
import PersonIcon from "@mui/icons-material/Person";
import RefreshIcon from "@mui/icons-material/Refresh";

export default function TopBar({ title, cameraConnected, onReset }) {
  return (
    <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", mb: 3 }}>
      <Typography variant="h5" fontWeight={700} color="primary.main">
        {title}
      </Typography>

      <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
        <Chip
          label={
            <Box>
              <Typography variant="caption" display="block" fontWeight={600}>
                Camera Status
              </Typography>
              <Typography variant="caption" color={cameraConnected ? "success.main" : "text.secondary"}>
                {cameraConnected ? "Connected" : "Disconnected"}
              </Typography>
            </Box>
          }
          sx={{ height: 48, px: 1, bgcolor: "background.paper", border: "1px solid #e2e8f0" }}
          icon={
            <Box
              sx={{
                width: 10,
                height: 10,
                borderRadius: "50%",
                bgcolor: cameraConnected ? "success.main" : "grey.400",
                ml: 1,
              }}
            />
          }
        />

        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          <Avatar sx={{ bgcolor: "primary.main" }}>
            <PersonIcon />
          </Avatar>
          <Box>
            <Typography variant="body2" fontWeight={600}>
              Admin User
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Administrator
            </Typography>
          </Box>
        </Box>

        {onReset && (
          <Button variant="contained" color="error" startIcon={<RefreshIcon />} onClick={onReset}>
            Reset Count
          </Button>
        )}
      </Box>
    </Box>
  );
}
