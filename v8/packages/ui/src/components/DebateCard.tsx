import { Card, CardContent, Typography, Chip, Box } from '@mui/material'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faChartLine } from '@fortawesome/free-solid-svg-icons'
import type { Debate } from '@stock-debate/types'

interface DebateCardProps {
  debate: Debate
  onClick?: () => void
}

export function DebateCard({ debate, onClick }: DebateCardProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success'
      case 'in_progress':
        return 'info'
      case 'failed':
        return 'error'
      default:
        return 'default'
    }
  }

  const getVerdictColor = (verdict: string | null) => {
    switch (verdict) {
      case 'BUY':
        return '#4caf50'
      case 'HOLD':
        return '#ff9800'
      case 'SELL':
        return '#f44336'
      default:
        return '#9e9e9e'
    }
  }

  return (
    <Card 
      sx={{ cursor: onClick ? 'pointer' : 'default', '&:hover': onClick ? { boxShadow: 3 } : {} }}
      onClick={onClick}
    >
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6" component="div" display="flex" alignItems="center" gap={1}>
            <FontAwesomeIcon icon={faChartLine} />
            {debate.symbol}
          </Typography>
          <Chip 
            label={debate.status.replace('_', ' ')} 
            color={getStatusColor(debate.status) as any}
            size="small"
          />
        </Box>
        
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Timeframe: {debate.timeframe.replace('_', ' ')}
        </Typography>
        
        {debate.verdict && (
          <Box mt={2} display="flex" gap={1} alignItems="center">
            <Typography variant="body2" fontWeight="bold">
              Verdict:
            </Typography>
            <Chip 
              label={debate.verdict}
              sx={{ 
                backgroundColor: getVerdictColor(debate.verdict),
                color: 'white',
                fontWeight: 'bold'
              }}
              size="small"
            />
            {debate.confidence && (
              <Chip 
                label={debate.confidence}
                variant="outlined"
                size="small"
              />
            )}
          </Box>
        )}
        
        <Typography variant="caption" color="text.secondary" display="block" mt={2}>
          Created: {new Date(debate.createdAt).toLocaleDateString()}
        </Typography>
      </CardContent>
    </Card>
  )
}
