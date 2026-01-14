import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { md3ColorScheme, md3Shape, md3Elevation } from '../../theme/md3';

interface NavItem {
  label: string;
  icon: string;
  path: string;
  badge?: number;
}

interface NavbarProps {
  items: NavItem[];
  title: string;
  onMenuToggle?: (open: boolean) => void;
}

/**
 * Material Design 3 Navigation Bar (Navbar)
 * Single-line toolbar with title and actions
 */
export const MD3Navbar: React.FC<NavbarProps> = ({ items, title, onMenuToggle }) => {
  const [menuOpen, setMenuOpen] = useState(false);

  const handleMenuToggle = () => {
    const newState = !menuOpen;
    setMenuOpen(newState);
    onMenuToggle?.(newState);
  };

  return (
    <nav
      style={{
        backgroundColor: md3ColorScheme.light.surface,
        color: md3ColorScheme.light.onSurface,
        boxShadow: md3Elevation.level1,
        padding: '12px 16px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        borderBottom: `1px solid ${md3ColorScheme.light.surfaceVariant}`,
      }}
    >
      {/* Left: Menu + Title */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <button
          onClick={handleMenuToggle}
          style={{
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            fontSize: '24px',
            color: md3ColorScheme.light.onSurface,
            padding: '8px',
            borderRadius: md3Shape.corner.medium,
            transition: 'background-color 0.2s',
          }}
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLButtonElement).style.backgroundColor =
              `rgba(103, 80, 164, ${0.08})`;
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLButtonElement).style.backgroundColor = 'transparent';
          }}
          title="Toggle menu"
        >
          <span className="fa-solid fa-bars" />
        </button>

        <span style={{ fontSize: '22px', fontWeight: 500 }}>{title}</span>
      </div>

      {/* Right: Action Items */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        {items.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            style={{
              textDecoration: 'none',
              color: md3ColorScheme.light.onSurface,
              padding: '8px 16px',
              borderRadius: md3Shape.corner.medium,
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              fontSize: '14px',
              fontWeight: 500,
              transition: 'background-color 0.2s',
              position: 'relative',
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLAnchorElement).style.backgroundColor =
                `rgba(103, 80, 164, ${0.08})`;
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLAnchorElement).style.backgroundColor = 'transparent';
            }}
          >
            <span className={`fa-solid ${item.icon}`} />
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
                  fontSize: '12px',
                  fontWeight: 'bold',
                }}
              >
                {item.badge}
              </span>
            )}
          </Link>
        ))}
      </div>
    </nav>
  );
};

export default MD3Navbar;
