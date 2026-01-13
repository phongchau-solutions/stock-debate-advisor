import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders analysis route by default', () => {
  render(<App />);
  expect(
    screen.getByRole('heading', { name: /Debate & Analysis/i })
  ).toBeInTheDocument();
});


