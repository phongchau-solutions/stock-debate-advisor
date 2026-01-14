import React, { useState } from 'react';
import { md3ColorScheme, md3Shape, md3StateOpacity } from '../../theme/md3';

interface CollapsibleMenuItem {
  label: string;
  icon: string;
  children?: CollapsibleMenuItem[];
  onClick?: () => void;
}

interface MD3CollapsibleMenuProps {
  items: CollapsibleMenuItem[];
  isOpen: boolean;
  onClose: () => void;
}

/**
 * Material Design 3 Collapsible Menu
 * Hierarchical navigation with collapsible sections
 */
export const MD3CollapsibleMenu: React.FC<MD3CollapsibleMenuProps> = ({
  items,
  isOpen,
  onClose,
}) => {
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());

  const toggleExpand = (label: string) => {
    const newExpanded = new Set(expandedItems);
    if (newExpanded.has(label)) {
      newExpanded.delete(label);
    } else {
      newExpanded.add(label);
    }
    setExpandedItems(newExpanded);
  };

  const renderMenuItem = (item: CollapsibleMenuItem, depth = 0) => {
    const isExpanded = expandedItems.has(item.label);
    const hasChildren = item.children && item.children.length > 0;

    return (
      <div key={item.label}>
        <button
          onClick={() => {
            if (hasChildren) {
              toggleExpand(item.label);
            }
            item.onClick?.();
          }}
          style={{
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            padding: `8px ${12 + depth * 16}px`,
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: 500,
            color: md3ColorScheme.light.onSurface,
            transition: 'background-color 0.2s, color 0.2s',
          }}
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLButtonElement).style.backgroundColor =
              `rgba(103, 80, 164, ${md3StateOpacity.hoverOpacity})`;
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLButtonElement).style.backgroundColor = 'transparent';
          }}
        >
          <span className={`fa-solid ${item.icon}`} style={{ width: '24px' }} />
          <span style={{ flex: 1, textAlign: 'left' }}>{item.label}</span>
          {hasChildren && (
            <span
              className="fa-solid fa-chevron-right"
              style={{
                fontSize: '12px',
                transition: 'transform 0.2s',
                transform: isExpanded ? 'rotate(90deg)' : 'rotate(0deg)',
              }}
            />
          )}
        </button>

        {/* Render children if expanded */}
        {hasChildren && isExpanded && (
          <div>
            {item.children!.map((child) => renderMenuItem(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  if (!isOpen) return null;

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        zIndex: 999,
      }}
      onClick={onClose}
    >
      {/* Overlay */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          backgroundColor: `rgba(0, 0, 0, 0.5)`,
        }}
      />

      {/* Menu Panel */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '280px',
          height: '100%',
          backgroundColor: md3ColorScheme.light.surface,
          boxShadow: md3ColorScheme.light.shadow,
          overflowY: 'auto',
          zIndex: 1000,
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div
          style={{
            padding: '16px',
            borderBottom: `1px solid ${md3ColorScheme.light.surfaceVariant}`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <h2 style={{ margin: 0, fontSize: '18px', fontWeight: 600 }}>Menu</h2>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              fontSize: '24px',
              color: md3ColorScheme.light.onSurface,
              padding: '4px',
            }}
          >
            <span className="fa-solid fa-xmark" />
          </button>
        </div>

        {/* Menu Items */}
        <div style={{ padding: '8px 0' }}>
          {items.map((item) => renderMenuItem(item))}
        </div>
      </div>
    </div>
  );
};

export default MD3CollapsibleMenu;
