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
import DownloadIcon from "@mui/icons-material/Download";
import TopBar from "../components/TopBar";
import { getDashboard, getDateWiseReport, resetCounts } from "../api";

function toISODate(d) {
  return d.toISOString().slice(0, 10);
}

export default function DateWiseReport() {
  const today = new Date();
  const weekAgo = new Date(today.getTime() - 6 * 86400000);

  const [from, setFrom] = useState(toISODate(weekAgo));
  const [to, setTo] = useState(toISODate(today));
  const [shift, setShift] = useState("");
  const [report, setReport] = useState(null);
  const [cameraConnected, setCameraConnected] = useState(false);

  const runSearch = async () => {
    const data = await getDateWiseReport({ from, to, shift: shift || undefined });
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
  };

  const handleReset = async () => {
    await resetCounts("manual reset from date wise report");
    runSearch();
    getDashboard().then((d) => setCameraConnected(d.camera_connected));
  };

  const exportCsv = () => {
    if (!report) return;
    const header = "Date,Shift 1,Shift 2,Total Count\n";
    const lines = report.rows
      .map((r) => `${r.report_date},${r.shift1_count},${r.shift2_count},${r.total_count}`)
      .join("\n");
    const blob = new Blob([header + lines], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `date-wise-report_${from}_to_${to}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <Box>
      <TopBar title="Date Wise Report" cameraConnected={cameraConnected} onReset={handleReset} />

      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={3}>
            <TextField label="From Date" type="date" fullWidth value={from} onChange={(e) => setFrom(e.target.value)} InputLabelProps={{ shrink: true }} />
          </Grid>
          <Grid item xs={12} sm={3}>
            <TextField label="To Date" type="date" fullWidth value={to} onChange={(e) => setTo(e.target.value)} InputLabelProps={{ shrink: true }} />
          </Grid>
          <Grid item xs={12} sm={2}>
            <TextField select label="Shift" fullWidth value={shift} onChange={(e) => setShift(e.target.value)}>
              <MenuItem value="">All Shifts</MenuItem>
              <MenuItem value="1">Shift 1</MenuItem>
              <MenuItem value="2">Shift 2</MenuItem>
            </TextField>
          </Grid>
          <Grid item xs={6} sm={2}>
            <Button variant="contained" fullWidth startIcon={<SearchIcon />} onClick={runSearch}>
              Search
            </Button>
          </Grid>
          <Grid item xs={6} sm={2}>
            <Button variant="outlined" fullWidth onClick={handleClear}>
              Clear
            </Button>
          </Grid>
        </Grid>
      </Paper>

      <Paper sx={{ p: 2 }}>
        <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2 }}>
          <Typography variant="subtitle1" fontWeight={700}>
            Date Wise Summary
          </Typography>
          <Button variant="outlined" startIcon={<DownloadIcon />} onClick={exportCsv}>
            Export
          </Button>
        </Box>

        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Date</TableCell>
              <TableCell align="right">Shift 1 (07:00 AM - 07:00 PM)</TableCell>
              <TableCell align="right">Shift 2 (07:00 PM - 07:00 AM)</TableCell>
              <TableCell align="right">Total Count</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {report?.rows.map((row) => (
              <TableRow key={row.report_date}>
                <TableCell>{row.report_date}</TableCell>
                <TableCell align="right">{row.shift1_count.toLocaleString()}</TableCell>
                <TableCell align="right">{row.shift2_count.toLocaleString()}</TableCell>
                <TableCell align="right">
                  <b>{row.total_count.toLocaleString()}</b>
                </TableCell>
              </TableRow>
            ))}
            {report && (
              <TableRow>
                <TableCell>
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
