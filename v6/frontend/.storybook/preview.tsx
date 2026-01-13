import type { Preview } from '@storybook/react';
import React from 'react';
import '../src/index.css';

const preview: Preview = {
  decorators: [
    (Story) => (
      <div className="min-h-screen bg-background text-foreground">
        <Story />
      </div>
    ),
  ],
};

export default preview;


