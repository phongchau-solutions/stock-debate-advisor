import React, { useState } from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import MD3Tabs from '../../components/md3/MD3Tabs';

const mockTabs = [
  { id: 'tab1', label: 'Financials', icon: 'fa-chart-line' },
  { id: 'tab2', label: 'Technical', icon: 'fa-arrow-trend-up' },
  { id: 'tab3', label: 'Sentiment', icon: 'fa-face-smile', badge: 5 },
  { id: 'tab4', label: 'News', icon: 'fa-newspaper', disabled: true },
];

const TabsWrapper = ({ onChange }: { onChange: (id: string) => void }) => {
  const [activeTab, setActiveTab] = useState('tab1');

  const handleChange = (id: string) => {
    setActiveTab(id);
    onChange(id);
  };

  return (
    <MD3Tabs items={mockTabs} activeTabId={activeTab} onChange={handleChange} variant="primary" />
  );
};

describe('MD3Tabs', () => {
  it('should render all tab items', () => {
    render(<TabsWrapper onChange={jest.fn()} />);

    expect(screen.getByText('Financials')).toBeInTheDocument();
    expect(screen.getByText('Technical')).toBeInTheDocument();
    expect(screen.getByText('Sentiment')).toBeInTheDocument();
    expect(screen.getByText('News')).toBeInTheDocument();
  });

  it('should display badge on tab', () => {
    render(<TabsWrapper onChange={jest.fn()} />);

    expect(screen.getByText('5')).toBeInTheDocument();
  });

  it('should call onChange when tab is clicked', () => {
    const handleChange = jest.fn();
    render(<TabsWrapper onChange={handleChange} />);

    fireEvent.click(screen.getByText('Technical'));

    expect(handleChange).toHaveBeenCalledWith('tab2');
  });

  it('should not click disabled tab', () => {
    const handleChange = jest.fn();
    render(<TabsWrapper onChange={handleChange} />);

    const newsButton = screen
      .getByText('News')
      .closest('button') as HTMLButtonElement;
    expect(newsButton.disabled).toBe(true);

    fireEvent.click(newsButton);
    expect(handleChange).not.toHaveBeenCalledWith('tab4');
  });

  it('should render icons if provided', () => {
    const { container } = render(<TabsWrapper onChange={jest.fn()} />);

    const icons = container.querySelectorAll('.fa-solid');
    expect(icons.length).toBeGreaterThan(0);
  });
});
