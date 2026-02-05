import { Outlet } from 'react-router-dom'
import { AppBar, Toolbar, Typography, Container, Box } from '@mui/material'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faChartLine } from '@fortawesome/free-solid-svg-icons'

export default function MainLayout() {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <AppBar position="static">
        <Toolbar>
          <FontAwesomeIcon icon={faChartLine} style={{ marginRight: '12px' }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Stock Debate Advisor
          </Typography>
        </Toolbar>
      </AppBar>
      <Container component="main" sx={{ mt: 4, mb: 4, flex: 1 }}>
        <Outlet />
      </Container>
    </Box>
  )
}
