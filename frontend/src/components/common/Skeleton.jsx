import React from 'react';
import './Skeleton.css';

export const Skeleton = ({ 
  width, 
  height, 
  variant = 'text', // 'text', 'circular', 'rectangular'
  className = '' 
}) => {
  const style = {
    width: width || (variant === 'text' ? '100%' : 'auto'),
    height: height || (variant === 'text' ? '1rem' : 'auto'),
  };

  return (
    <div 
      className={`skeleton skeleton-${variant} ${className}`}
      style={style}
      aria-hidden="true"
    />
  );
};

export const SkeletonText = ({ lines = 3, gap = '0.75rem', lastWidth = '70%' }) => {
  return (
    <div className="skeleton-text-container" style={{ gap }}>
      {[...Array(lines)].map((_, i) => (
        <Skeleton 
          key={i} 
          variant="text" 
          width={i === lines - 1 ? lastWidth : '100%'} 
        />
      ))}
    </div>
  );
};
