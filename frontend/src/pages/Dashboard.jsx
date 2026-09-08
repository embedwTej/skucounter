import { useEffect, useState, useCallback } from "react";
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Button,
  Paper,
} from "@mui/material";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { useNavigate } from "react-router-dom";
import TopBar from "../components/TopBar";
import { getDashboard, resetCounts } from "../api";

const POLL_MS = 5000;

function StatCard({ label, value, sub }) {
  return (
    <Card>
      <CardContent>
        <Typography variant="body2" color="text.secondary">
          {label}
        </Typography>
        <Typography variant="h4" fontWeight={700} sx={{ mt: 0.5 }}>
          {value}
        </Typography>
        {sub && (
          <Typography variant="caption" color="text.secondary">
            {sub}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
}

export default function Dashboard() {
  const [data, setData] = useState(null);
  const navigate = useNavigate();

  const load = useCallback(async () => {
    try {
      const d = await getDashboard();
      setData(d);
    } catch (e) {
      console.error(e);
    }
  }, []);

  useEffect(() => {
    load();
    const id = setInterval(load, POLL_MS);
    return () => clearInterval(id);
  }, [load]);

  const handleReset = async () => {
    await resetCounts("manual reset from dashboard");
    load();
  };

  if (!data) {
    return <Typography>Loading…</Typography>;
  }

  return (
    <Box>
      <TopBar title="Dashboard" cameraConnected={data.camera_connected} onReset={handleReset} />

      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard label="Total Count (All SKUs)" value={data.total_count.toLocaleString()} sub="Cumulative Count" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard label="SKUs Detected" value={data.skus_detected} sub="Across all SKUs" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard label="Current Shift" value={`Shift ${data.current_shift}`} sub={data.current_shift_label} />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            label="Last Updated"
            value={data.last_updated ? new Date(data.last_updated).toLocaleTimeString() : "—"}
            sub={data.last_updated ? new Date(data.last_updated).toLocaleDateString() : ""}
          />
        </Grid>
      </Grid>

      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: "100%" }}>
            <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 1 }}>
              SKU Wise Count
            </Typography>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>#</TableCell>
                  <TableCell>SKU Code</TableCell>
                  <TableCell>SKU Name</TableCell>
                  <TableCell align="right">Count</TableCell>
                  <TableCell align="right">% of Total</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {data.sku_counts.map((row, i) => (
                  <TableRow key={row.sku_code}>
                    <TableCell>{i + 1}</TableCell>
                    <TableCell>{row.sku_code}</TableCell>
                    <TableCell>{row.sku_name || "—"}</TableCell>
                    <TableCell align="right">{row.count.toLocaleString()}</TableCell>
                    <TableCell align="right">{row.pct_of_total}%</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            <Button sx={{ mt: 2 }} onClick={() => navigate("/reports/sku-wise")}>
              View SKU Wise Report →
            </Button>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: "100%" }}>
            <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 1 }}>
              Count Summary
            </Typography>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={data.sku_counts}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="sku_code" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#2563eb" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
            <Box sx={{ display: "flex", justifyContent: "space-between", mt: 2, p: 1.5, bgcolor: "#eef2ff", borderRadius: 1 }}>
              <Typography fontWeight={600}>Total Count</Typography>
              <Typography fontWeight={700}>{data.total_count.toLocaleString()}</Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      <Paper sx={{ p: 2 }}>
        <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 2 }}>
          Reports
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <Card variant="outlined" sx={{ p: 2 }}>
              <Typography fontWeight={700}>Date Wise Report</Typography>
              <Typography variant="body2" color="text.secondary" sx={{ my: 1 }}>
                View counts and summaries for a selected date or date range.
              </Typography>
              <Button onClick={() => navigate("/reports/date-wise")}>View Report →</Button>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Card variant="outlined" sx={{ p: 2 }}>
              <Typography fontWeight={700}>SKU Wise Report</Typography>
              <Typography variant="body2" color="text.secondary" sx={{ my: 1 }}>
                View detailed count and performance for each SKU.
              </Typography>
              <Button onClick={() => navigate("/reports/sku-wise")}>View Report →</Button>
            </Card>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
}
