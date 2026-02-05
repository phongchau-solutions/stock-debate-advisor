import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import { Routes, Route } from 'react-router-dom'
import MainLayout from './components/layouts/MainLayout'
import Login from './features/auth/Login'

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#6750A4',
    },
    secondary: {
      main: '#625B71',
    },
  },
})

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<div>Dashboard</div>} />
          <Route path="login" element={<Login />} />
        </Route>
      </Routes>
    </ThemeProvider>
  )
}

export default App
