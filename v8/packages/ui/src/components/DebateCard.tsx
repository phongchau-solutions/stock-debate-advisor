import { Card, CardContent, Typography, Chip, Box } from '@mui/material'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faCheck, faClock, faXmark } from '@fortawesome/free-solid-svg-icons'
import { Debate, DebateStatus } from '@stock-debate/types'

interface DebateCardProps {
  debate: Debate
  onClick?: () => void
}

export function DebateCard({ debate, onClick }: DebateCardProps) {
  const statusIcon = {
    [DebateStatus.PENDING]: faClock,
    [DebateStatus.IN_PROGRESS]: faClock,
    [DebateStatus.COMPLETED]: faCheck,
    [DebateStatus.FAILED]: faXmark,
  }[debate.status]

  const statusColor = {
    [DebateStatus.PENDING]: 'default',
    [DebateStatus.IN_PROGRESS]: 'info',
    [DebateStatus.COMPLETED]: 'success',
    [DebateStatus.FAILED]: 'error',
  }[debate.status] as 'default' | 'info' | 'success' | 'error'

  return (
    <Card
      sx={{ cursor: onClick ? 'pointer' : 'default' }}
      onClick={onClick}
    >
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6" component="div">
            {debate.symbol}
          </Typography>
          <Chip
            icon={<FontAwesomeIcon icon={statusIcon} />}
            label={debate.status}
            color={statusColor}
            size="small"
          />
        </Box>
        
        <Typography color="text.secondary" gutterBottom>
          Timeframe: {debate.timeframe.replace('_', ' ')}
        </Typography>
        
        {debate.verdict && (
          <Box mt={2}>
            <Chip
              label={debate.verdict}
              color={
                debate.verdict === 'BUY'
                  ? 'success'
                  : debate.verdict === 'SELL'
                  ? 'error'
                  : 'warning'
              }
            />
            {debate.confidence && (
              <Chip
                label={`${debate.confidence} confidence`}
                variant="outlined"
                size="small"
                sx={{ ml: 1 }}
              />
            )}
          </Box>
        )}
      </CardContent>
    </Card>
  )
}
