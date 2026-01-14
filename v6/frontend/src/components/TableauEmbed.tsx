import React, { useEffect, useState } from 'react';

interface TableauEmbedProps {
  name: string;
  description?: string;
  height?: number;
}

/**
 * Tableau Public Embed Component
 * Embeds Tableau dashboards using Tableau's embed API
 */
export const TableauEmbed: React.FC<TableauEmbedProps> = ({
  name,
  description,
  height = 700,
}) => {
  const vizId = `viz-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  const [containerWidth, setContainerWidth] = useState(0);

  useEffect(() => {
    // Load Tableau embed script
    const script = document.createElement('script');
    script.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';
    script.async = true;
    script.onload = () => {
      if ((window as any).tableau) {
        (window as any).tableau.Viz.createDestroyDestroyTableauInstances();
      }
    };
    document.body.appendChild(script);

    // Handle responsive sizing
    const container = document.getElementById(vizId);
    if (container) {
      setContainerWidth(container.offsetWidth);
      const handleResize = () => {
        setContainerWidth(container.offsetWidth);
      };
      window.addEventListener('resize', handleResize);
      return () => window.removeEventListener('resize', handleResize);
    }
  }, [vizId]);

  // Calculate responsive dimensions
  const vizElement = document.getElementById(vizId);
  let minWidth = 1000;
  let maxWidth = '100%';
  let minHeight = height;
  let maxHeight = height;

  if (containerWidth > 800) {
    minWidth = 1564;
    maxWidth = '100%';
    minHeight = height;
    maxHeight = height;
  } else if (containerWidth > 500) {
    minWidth = 1000;
    maxWidth = '100%';
    minHeight = height;
    maxHeight = height;
  } else {
    minWidth = '100%';
    maxWidth = '100%';
    minHeight = height * 1.5;
    maxHeight = height * 1.5;
  }

  return (
    <div className="rounded-md overflow-hidden border border-border/50 bg-white dark:bg-slate-900">
      <div
        id={vizId}
        className="tableauPlaceholder w-full"
        style={{
          position: 'relative',
          width: '100%',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: `${height}px`,
        }}
      >
        <noscript>
          <a href="#" className="text-muted-foreground text-sm">
            Tableau visualization requires JavaScript
          </a>
        </noscript>
        <object
          className="tableauViz"
          style={{
            display: 'none',
          }}
        >
          <param name="host_url" value="https%3A%2F%2Fpublic.tableau.com%2F" />
          <param name="embed_code_version" value="3" />
          <param name="site_root" value="" />
          <param name="name" value={name} />
          <param name="tabs" value="yes" />
          <param name="toolbar" value="yes" />
          <param name="static_image" value="" />
          <param name="animate_transition" value="yes" />
          <param name="display_static_image" value="yes" />
          <param name="display_spinner" value="yes" />
          <param name="display_overlay" value="yes" />
          <param name="display_count" value="yes" />
          <param name="language" value="en-US" />
        </object>
      </div>
      {description && (
        <div className="px-4 py-2 bg-muted/50 border-t border-border/50">
          <p className="text-xs text-muted-foreground">{description}</p>
        </div>
      )}
    </div>
  );
};
