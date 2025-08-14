import { render, screen } from '@testing-library/react';
import App from './App';

test('renders Dashboard button', () => {
  render(<App />);
  const dashboardElement = screen.getByText(/Dashboard/i);
  expect(dashboardElement).toBeInTheDocument();
});
