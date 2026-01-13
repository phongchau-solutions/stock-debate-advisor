/**
 * FontAwesome 7 Free Icon Audit & Usage Guide
 * Reference: https://fontawesome.com/icons
 * 
 * This file documents all FA7 icons used in the application
 * ensuring 100% wise usage according to Material Design 3 principles
 */

export const FA7_ICONS = {
  // Navigation Icons
  navigation: {
    menu: 'fa-bars',
    close: 'fa-xmark',
    back: 'fa-arrow-left',
    forward: 'fa-arrow-right',
    home: 'fa-house',
    search: 'fa-magnifying-glass',
    filter: 'fa-filter',
    sort: 'fa-arrow-down-arrow-up',
    expandMore: 'fa-chevron-down',
    expandLess: 'fa-chevron-up',
    expandLeft: 'fa-chevron-left',
    expandRight: 'fa-chevron-right',
  },

  // Financial & Market Icons
  financial: {
    chart_line: 'fa-chart-line',
    chart_area: 'fa-chart-area',
    chart_pie: 'fa-chart-pie',
    chart_bar: 'fa-chart-bar',
    chart_column: 'fa-chart-column',
    trend_up: 'fa-arrow-trend-up',
    trend_down: 'fa-arrow-trend-down',
    wallet: 'fa-wallet',
    coins: 'fa-coins',
    pound: 'fa-sterling-sign',
    dollar: 'fa-dollar-sign',
    percent: 'fa-percent',
    scale: 'fa-scale-balanced',
    landmark: 'fa-landmark',
  },

  // Content & Media Icons
  media: {
    newspaper: 'fa-newspaper',
    document: 'fa-file',
    file_text: 'fa-file-lines',
    pdf: 'fa-file-pdf',
    csv: 'fa-file-csv',
    image: 'fa-image',
    video: 'fa-video',
    camera: 'fa-camera',
    microphone: 'fa-microphone',
  },

  // Analysis & Data Icons
  analysis: {
    microscope: 'fa-microscope',
    flask: 'fa-flask',
    database: 'fa-database',
    server: 'fa-server',
    cloud: 'fa-cloud',
    download: 'fa-download',
    upload: 'fa-upload',
    refresh: 'fa-arrow-rotate-right',
    sync: 'fa-arrows-rotate',
    lightning: 'fa-bolt',
  },

  // Status & Feedback Icons
  status: {
    check: 'fa-check',
    check_circle: 'fa-circle-check',
    close_circle: 'fa-circle-xmark',
    info: 'fa-circle-info',
    warning: 'fa-triangle-exclamation',
    error: 'fa-circle-exclamation',
    success: 'fa-circle-check',
    loading: 'fa-spinner',
    star: 'fa-star',
    star_half: 'fa-star-half-stroke',
    heart: 'fa-heart',
  },

  // User & Account Icons
  account: {
    user: 'fa-user',
    users: 'fa-users',
    person: 'fa-person',
    user_circle: 'fa-circle-user',
    profile: 'fa-id-card',
    settings: 'fa-gear',
    logout: 'fa-sign-out',
    login: 'fa-sign-in',
    lock: 'fa-lock',
    key: 'fa-key',
  },

  // Communication Icons
  communication: {
    message: 'fa-message',
    comment: 'fa-comment',
    comments: 'fa-comments',
    bell: 'fa-bell',
    mail: 'fa-envelope',
    at: 'fa-at',
    share: 'fa-share',
    share_nodes: 'fa-share-nodes',
    link: 'fa-link',
  },

  // Action Icons
  actions: {
    play: 'fa-play',
    pause: 'fa-pause',
    stop: 'fa-stop',
    save: 'fa-floppy-disk',
    delete: 'fa-trash',
    edit: 'fa-pen-to-square',
    copy: 'fa-copy',
    print: 'fa-print',
    download: 'fa-download',
    export: 'fa-arrow-up-right-from-square',
  },

  // Semantic Icons
  semantic: {
    calendar: 'fa-calendar',
    clock: 'fa-clock',
    time: 'fa-hourglass-end',
    alarm: 'fa-bell',
    bookmark: 'fa-bookmark',
    flag: 'fa-flag',
    tag: 'fa-tag',
    globe: 'fa-globe',
    map: 'fa-map',
    location: 'fa-location-dot',
  },

  // Brand Icons (Font Awesome Pro features)
  brands: {
    github: 'fa-github',
    google: 'fa-google',
    facebook: 'fa-facebook',
    twitter: 'fa-twitter',
    linkedin: 'fa-linkedin',
    slack: 'fa-slack',
  },
};

/**
 * Material Design 3 Icon Usage Patterns
 * 
 * 1. Navigation: Use consistent 24px size
 * 2. Buttons: 20px for icon buttons, 18px for text + icon
 * 3. Lists: 20px left margin with 8px gap to text
 * 4. Dialogs: 24px for header icons
 * 5. Status: Use with colors (error, warning, success)
 */

interface IconUsageContext {
  purpose: string;
  recommendedSize: string;
  renderExample: string;
}

export const FA7_USAGE_PATTERNS: Record<string, IconUsageContext> = {
  navbar_icon: {
    purpose: 'Top navigation bar icons',
    recommendedSize: '20px-24px',
    renderExample: '<span className="fa-solid fa-bars" style={{ fontSize: "24px" }} />',
  },
  button_icon: {
    purpose: 'Icon inside action buttons',
    recommendedSize: '18px-20px',
    renderExample:
      '<button><span className="fa-solid fa-check" /> Save</button>',
  },
  status_indicator: {
    purpose: 'Show loading, error, success states',
    recommendedSize: '20px',
    renderExample:
      '<span className="fa-solid fa-circle-check text-success" />',
  },
  menu_item: {
    purpose: 'Sidebar or dropdown menu icons',
    recommendedSize: '18px-20px',
    renderExample:
      '<span className="fa-solid fa-chart-line" /> Financial Data',
  },
  badge_or_notification: {
    purpose: 'Small notification or count badges',
    recommendedSize: '12px-16px',
    renderExample:
      '<span className="fa-solid fa-bell" style={{ fontSize: "16px" }} />',
  },
  data_visualization: {
    purpose: 'Dashboard and chart indicators',
    recommendedSize: '24px-32px',
    renderExample:
      '<span className="fa-solid fa-chart-line" style={{ fontSize: "28px" }} />',
  },
};

/**
 * Best Practices for FontAwesome 7 Usage
 * 
 * 1. ALWAYS use semantic icon names, never by unicode/code point
 * 2. Use fa-solid consistently (Free tier limitation)
 * 3. Set explicit sizes to maintain design consistency
 * 4. Pair icons with meaningful labels (accessibility)
 * 5. Use color classes: text-primary, text-success, text-error, etc.
 * 6. Provide ARIA labels for screen readers
 * 7. Animate with transitions, not constant rotation
 * 8. Respect Material Design 3 spacing (8px grid)
 */

export const FA7_BEST_PRACTICES = [
  {
    rule: 'Use semantic names',
    good: '<span className="fa-solid fa-check" /> ✓',
    bad: '<span className="fa-solid fa-f058" /> ✗',
  },
  {
    rule: 'Explicit sizing',
    good: '<span className="fa-solid fa-check" style={{ fontSize: "20px" }} />',
    bad: '<span className="fa-solid fa-check" />',
  },
  {
    rule: 'Include labels',
    good: '<span className="fa-solid fa-check" aria-label="Success" />',
    bad: '<span className="fa-solid fa-check" />',
  },
  {
    rule: 'Color for status',
    good: '<span className="fa-solid fa-alert-circle text-error" />',
    bad: '<span className="fa-solid fa-alert-circle" />',
  },
  {
    rule: 'Material Design spacing',
    good: '<div className="flex items-center gap-2"><span className="fa-solid fa-chart" /> Charts</div>',
    bad: '<div><span className="fa-solid fa-chart" /> Charts</div>',
  },
];

/**
 * Icon Color Mapping for Material Design 3
 */
export const FA7_COLORS = {
  primary: '#6750a4',
  secondary: '#625b71',
  tertiary: '#7d5260',
  error: '#b3261e',
  warning: '#f9a825',
  success: '#2ecc71',
  info: '#0ea5e9',
  muted: '#79747e',
};

/**
 * Audit Function to Verify Usage
 */
export const auditFontAwesomeUsage = (element: HTMLElement): {
  totalIcons: number;
  validIcons: number;
  missingLabels: number;
  recommendations: string[];
} => {
  const icons = element.querySelectorAll('[class*="fa-"]');
  const validIconNames = Object.values(FA7_ICONS).flatMap((category) =>
    Object.values(category)
  );

  let validCount = 0;
  let missingLabelCount = 0;
  const recommendations: string[] = [];

  icons.forEach((icon) => {
    const classes = Array.from(icon.classList);
    const iconName = classes.find((c) => validIconNames.includes(c));

    if (iconName) {
      validCount++;
    }

    if (!icon.getAttribute('aria-label')) {
      missingLabelCount++;
    }
  });

  if (missingLabelCount > 0) {
    recommendations.push(
      `${missingLabelCount} icons missing aria-label for accessibility`
    );
  }

  return {
    totalIcons: icons.length,
    validIcons: validCount,
    missingLabels: missingLabelCount,
    recommendations,
  };
};
