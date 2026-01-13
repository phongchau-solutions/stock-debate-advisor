import React, { useState } from 'react';
import { md3ColorScheme, md3Shape, md3StateOpacity, md3Elevation } from '../../theme/md3';

interface TabItem {
  id: string;
  label: string;
  icon?: string;
  badge?: number;
  disabled?: boolean;
}

interface MD3TabsProps {
  items: TabItem[];
  activeTabId: string;
  onChange: (tabId: string) => void;
  variant?: 'primary' | 'secondary';
}

/**
 * Material Design 3 Tabs Component
 * Scrollable or fixed tabs with icons and badges
 */
export const MD3Tabs: React.FC<MD3TabsProps> = ({
  items,
  activeTabId,
  onChange,
  variant = 'primary',
}) => {
  const [scrollPosition, setScrollPosition] = useState(0);

  const isPrimaryVariant = variant === 'primary';
  const activeBgColor = isPrimaryVariant
    ? md3ColorScheme.light.primaryContainer
    : md3ColorScheme.light.secondaryContainer;
  const activeTextColor = isPrimaryVariant
    ? md3ColorScheme.light.onPrimaryContainer
    : md3ColorScheme.light.onSecondaryContainer;

  const tabsRef = React.useRef<HTMLDivElement>(null);

  const handleScroll = (direction: 'left' | 'right') => {
    if (!tabsRef.current) return;
    const scrollAmount = 200;
    const newPosition = scrollPosition + (direction === 'right' ? scrollAmount : -scrollAmount);
    tabsRef.current.scrollLeft = newPosition;
    setScrollPosition(newPosition);
  };

  return (
    <div
      style={{
        backgroundColor: md3ColorScheme.light.surface,
        borderBottom: `1px solid ${md3ColorScheme.light.surfaceVariant}`,
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        padding: '0 8px',
        position: 'relative',
      }}
    >
      {/* Scroll Left Button */}
      {scrollPosition > 0 && (
        <button
          onClick={() => handleScroll('left')}
          style={{
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            fontSize: '18px',
            color: md3ColorScheme.light.primary,
            padding: '12px 8px',
            flexShrink: 0,
          }}
        >
          <span className="fa-solid fa-chevron-left" />
        </button>
      )}

      {/* Tabs Container */}
      <div
        ref={tabsRef}
        style={{
          display: 'flex',
          gap: '8px',
          overflowX: 'auto',
          flex: 1,
          scrollBehavior: 'smooth',
          scrollbarWidth: 'none',
          msOverflowStyle: 'none',
        } as React.CSSProperties & { scrollbarWidth: string; msOverflowStyle: string }}
      >
        {/* Hide scrollbar */}
        <style>{`
          div::-webkit-scrollbar {
            display: none;
          }
        `}</style>

        {items.map((item) => {
          const isActive = item.id === activeTabId;

          return (
            <button
              key={item.id}
              disabled={item.disabled}
              onClick={() => !item.disabled && onChange(item.id)}
              style={{
                backgroundColor: isActive ? activeBgColor : 'transparent',
                color: isActive ? activeTextColor : md3ColorScheme.light.onSurface,
                border: 'none',
                cursor: item.disabled ? 'not-allowed' : 'pointer',
                padding: '12px 16px',
                borderRadius: md3Shape.corner.medium,
                fontSize: '14px',
                fontWeight: 500,
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                whiteSpace: 'nowrap',
                transition: 'all 0.2s',
                opacity: item.disabled ? 0.38 : 1,
                position: 'relative',
                flexShrink: 0,
              }}
              onMouseEnter={(e) => {
                if (!item.disabled && !isActive) {
                  (e.currentTarget as HTMLButtonElement).style.backgroundColor =
                    `rgba(103, 80, 164, ${md3StateOpacity.hoverOpacity})`;
                }
              }}
              onMouseLeave={(e) => {
                if (!isActive) {
                  (e.currentTarget as HTMLButtonElement).style.backgroundColor = 'transparent';
                }
              }}
              title={item.label}
            >
              {item.icon && <span className={`fa-solid ${item.icon}`} />}
              <span>{item.label}</span>
              {item.badge && (
                <span
                  style={{
                    backgroundColor: md3ColorScheme.light.error,
                    color: md3ColorScheme.light.onError,
                    borderRadius: '50%',
                    width: '20px',
                    height: '20px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '11px',
                    fontWeight: 'bold',
                    marginLeft: '4px',
                  }}
                >
                  {item.badge > 99 ? '99+' : item.badge}
                </span>
              )}
              {isActive && (
                <div
                  style={{
                    position: 'absolute',
                    bottom: '-1px',
                    left: 0,
                    right: 0,
                    height: '3px',
                    backgroundColor: isPrimaryVariant
                      ? md3ColorScheme.light.primary
                      : md3ColorScheme.light.secondary,
                    borderRadius: md3Shape.corner.small,
                  }}
                />
              )}
            </button>
          );
        })}
      </div>

      {/* Scroll Right Button */}
      <button
        onClick={() => handleScroll('right')}
        style={{
          background: 'none',
          border: 'none',
          cursor: 'pointer',
          fontSize: '18px',
          color: md3ColorScheme.light.primary,
          padding: '12px 8px',
          flexShrink: 0,
        }}
      >
        <span className="fa-solid fa-chevron-right" />
      </button>
    </div>
  );
};

export default MD3Tabs;
