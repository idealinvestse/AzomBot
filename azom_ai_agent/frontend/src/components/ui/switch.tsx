import React from 'react'

interface SwitchProps extends React.InputHTMLAttributes<HTMLInputElement> {}

export function Switch({ className, checked, onCheckedChange, ...props }: SwitchProps & { onCheckedChange?: (checked: boolean) => void }) {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onCheckedChange?.(e.target.checked)
  }
  return (
    <label className="relative inline-flex items-center cursor-pointer">
      <input
        type="checkbox"
        className="sr-only peer"
        checked={checked}
        onChange={handleChange}
        {...props}
      />
      <div
        className={`w-11 h-6 bg-input rounded-full peer peer-checked:bg-primary peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-background after:rounded-full after:h-5 after:w-5 after:transition-all ${className || ''}`}
      ></div>
    </label>
  )
}
