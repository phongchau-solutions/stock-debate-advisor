import { Alert, AlertTitle } from '@mui/material'

interface ErrorAlertProps {
  error: string | Error
  title?: string
}

export function ErrorAlert({ error, title = 'Error' }: ErrorAlertProps) {
  const message = typeof error === 'string' ? error : error.message

  return (
    <Alert severity="error">
      <AlertTitle>{title}</AlertTitle>
      {message}
    </Alert>
  )
}
