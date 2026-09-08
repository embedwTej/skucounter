import { useEffect, useState } from "react";
import {
  Box,
  Paper,
  Grid,
  TextField,
  MenuItem,
  Button,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Typography,
} from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import TopBar from "../components/TopBar";
import { getDashboard, getSkuWiseReport, resetCounts } from "../api";

function toISODate(d) {
  return d.toISOString().slice(0, 10);
}

export default function SkuWiseReport() {
  const today = new Date();
  const weekAgo = new Date(today.getTime() - 6 * 86400000);

  const [from, setFrom] = useState(toISODate(weekAgo));
  const [to, setTo] = useState(toISODate(today));
  const [shift, setShift] = useState("");
  const [sku, setSku] = useState("");
  const [report, setReport] = useState(null);
  const [cameraConnected, setCameraConnected] = useState(false);

  const runSearch = async () => {
    const data = await getSkuWiseReport({ from, to, shift: shift || undefined, sku: sku || undefined });
    setReport(data);
  };

  useEffect(() => {
    runSearch();
    getDashboard().then((d) => setCameraConnected(d.camera_connected));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleClear = () => {
    setFrom(toISODate(weekAgo));
    setTo(toISODate(today));
    setShift("");
    setSku("");
  };

  const handleReset = async () => {
    await resetCounts("manual reset from sku wise report");
    runSearch();
    getDashboard().then((d) => setCameraConnected(d.camera_connected));
  };

  const skuOptions = report ? Array.from(new Set(report.rows.map((r) => r.sku_code))) : [];

  return (
    <Box>
      <TopBar title="SKU Wise Report" cameraConnected={cameraConnected} onReset={handleReset} />

      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={2.5}>
            <TextField label="From Date" type="date" fullWidth value={from} onChange={(e) => setFrom(e.target.value)} InputLabelProps={{ shrink: true }} />
          </Grid>
          <Grid item xs={12} sm={2.5}>
            <TextField label="To Date" type="date" fullWidth value={to} onChange={(e) => setTo(e.target.value)} InputLabelProps={{ shrink: true }} />
          </Grid>
          <Grid item xs={12} sm={2}>
            <TextField select label="Shift" fullWidth value={shift} onChange={(e) => setShift(e.target.value)}>
              <MenuItem value="">All Shifts</MenuItem>
              <MenuItem value="1">Shift 1</MenuItem>
              <MenuItem value="2">Shift 2</MenuItem>
            </TextField>
          </Grid>
          <Grid item xs={12} sm={2}>
            <TextField select label="SKU" fullWidth value={sku} onChange={(e) => setSku(e.target.value)}>
              <MenuItem value="">All SKUs</MenuItem>
              {skuOptions.map((code) => (
                <MenuItem key={code} value={code}>
                  {code}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
          <Grid item xs={6} sm={1.5}>
            <Button variant="contained" fullWidth startIcon={<SearchIcon />} onClick={runSearch}>
              Search
            </Button>
          </Grid>
          <Grid item xs={6} sm={1.5}>
            <Button variant="outlined" fullWidth onClick={handleClear}>
              Clear
            </Button>
          </Grid>
        </Grid>
      </Paper>

      <Paper sx={{ p: 2 }}>
        <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 2 }}>
          SKU Wise Summary
        </Typography>

        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>#</TableCell>
              <TableCell>SKU Code</TableCell>
              <TableCell>SKU Name</TableCell>
              <TableCell>Shape</TableCell>
              <TableCell align="right">Shift 1 (07:00 AM - 07:00 PM)</TableCell>
              <TableCell align="right">Shift 2 (07:00 PM - 07:00 AM)</TableCell>
              <TableCell align="right">Total Count</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {report?.rows.map((row, i) => (
              <TableRow key={row.sku_code}>
                <TableCell>{i + 1}</TableCell>
                <TableCell>{row.sku_code}</TableCell>
                <TableCell>{row.sku_name || "—"}</TableCell>
                <TableCell>{row.shape || "—"}</TableCell>
                <TableCell align="right">{row.shift1_count.toLocaleString()}</TableCell>
                <TableCell align="right">{row.shift2_count.toLocaleString() || "-"}</TableCell>
                <TableCell align="right">
                  <b>{row.total_count.toLocaleString()}</b>
                </TableCell>
              </TableRow>
            ))}
            {report && (
              <TableRow>
                <TableCell colSpan={4}>
                  <b>Total</b>
                </TableCell>
                <TableCell align="right">
                  <b>{report.total_shift1.toLocaleString()}</b>
                </TableCell>
                <TableCell align="right">
                  <b>{report.total_shift2.toLocaleString()}</b>
                </TableCell>
                <TableCell align="right">
                  <b>{report.grand_total.toLocaleString()}</b>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
        {report && report.rows.length === 0 && (
          <Typography sx={{ mt: 2 }} color="text.secondary">
            No data for the selected range.
          </Typography>
        )}
      </Paper>
    </Box>
  );
}
