import { Alert, AlertTitle } from '@mui/material'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faTriangleExclamation } from '@fortawesome/free-solid-svg-icons'

interface ErrorAlertProps {
  title?: string
  message: string
  onClose?: () => void
}

export function ErrorAlert({ title = 'Error', message, onClose }: ErrorAlertProps) {
  return (
    <Alert
      severity="error"
      onClose={onClose}
      icon={<FontAwesomeIcon icon={faTriangleExclamation} />}
    >
      <AlertTitle>{title}</AlertTitle>
      {message}
    </Alert>
  )
}
