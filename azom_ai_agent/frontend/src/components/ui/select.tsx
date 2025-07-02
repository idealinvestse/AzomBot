import React, { createContext, useContext, useState, useEffect, useRef } from 'react'

interface SelectContextType {
  value: string
  onValueChange: (value: string) => void
  open: boolean
  setOpen: (open: boolean) => void
  triggerRef: React.RefObject<HTMLDivElement>
}

const SelectContext = createContext<SelectContextType | undefined>(undefined)

function useSelect() {
  const context = useContext(SelectContext)
  if (context === undefined) {
    throw new Error('useSelect must be used within a Select provider')
  }
  return context
}

export function Select({
  value,
  onValueChange,
  defaultValue,
  children
}: {
  value?: string
  onValueChange?: (value: string) => void
  defaultValue?: string
  children: React.ReactNode
}) {
  const [internalValue, setInternalValue] = useState(defaultValue || '')
  const [open, setOpen] = useState(false)
  const triggerRef = useRef<HTMLDivElement>(null)

  const handleValueChange = (newValue: string) => {
    if (onValueChange) {
      onValueChange(newValue)
    } else {
      setInternalValue(newValue)
    }
    setOpen(false)
  }

  const currentValue = value !== undefined ? value : internalValue

  return (
    <SelectContext.Provider
      value={{
        value: currentValue,
        onValueChange: handleValueChange,
        open,
        setOpen,
        triggerRef
      }}
    >
      {children}
    </SelectContext.Provider>
  )
}

export function SelectTrigger({ className, children, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  const { open, setOpen, triggerRef } = useSelect()

  return (
    <div
      ref={triggerRef}
      className={`flex items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 ${className || ''}`}
      onClick={() => setOpen(!open)}
      {...props}
    >
      {children}
      <svg
        width="15"
        height="15"
        viewBox="0 0 15 15"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className={`h-4 w-4 opacity-50 transition-transform ${open ? 'rotate-180' : ''}`}
      >
        <path
          d="M4.93179 5.43179C4.75605 5.60753 4.75605 5.89245 4.93179 6.06819C5.10753 6.24392 5.39245 6.24392 5.56819 6.06819L7.49999 4.13638L9.43179 6.06819C9.60753 6.24392 9.89245 6.24392 10.0682 6.06819C10.2439 5.89245 10.2439 5.60753 10.0682 5.43179L7.81819 3.18179C7.73379 3.0974 7.61934 3.04999 7.49999 3.04999C7.38064 3.04999 7.26618 3.0974 7.18179 3.18179L4.93179 5.43179ZM10.0682 9.56819C10.2439 9.39245 10.2439 9.10753 10.0682 8.93179C9.89245 8.75606 9.60753 8.75606 9.43179 8.93179L7.49999 10.8636L5.56819 8.93179C5.39245 8.75606 5.10753 8.75606 4.93179 8.93179C4.75605 9.10753 4.75605 9.39245 4.93179 9.56819L7.18179 11.8182C7.26618 11.9026 7.38064 11.95 7.49999 11.95C7.61934 11.95 7.73379 11.9026 7.81819 11.8182L10.0682 9.56819Z"
          fill="currentColor"
          fillRule="evenodd"
          clipRule="evenodd"
        ></path>
      </svg>
    </div>
  )
}

export function SelectValue({ placeholder }: { placeholder?: string }) {
  const { value } = useSelect()
  return <span className="flex-1">{value || placeholder || 'Välj...'}</span>
}

export function SelectContent({ children, className }: { children: React.ReactNode; className?: string }) {
  const { open, triggerRef } = useSelect()
  const [style, setStyle] = useState<React.CSSProperties>({})

  useEffect(() => {
    if (open && triggerRef.current) {
      const rect = triggerRef.current.getBoundingClientRect()
      setStyle({
        position: 'absolute',
        top: `${rect.bottom + window.scrollY + 8}px`,
        left: `${rect.left + window.scrollX}px`,
        width: `${rect.width}px`,
        maxHeight: '300px',
        overflowY: 'auto',
        backgroundColor: 'var(--background)',
        border: '1px solid var(--border)',
        borderRadius: '6px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
        zIndex: 50
      })
    }
  }, [open, triggerRef])

  if (!open) return null

  return (
    <div style={style} className={className} onClick={(e) => e.stopPropagation()}>
      {children}
    </div>
  )
}

export function SelectItem({ value, children }: { value: string; children: React.ReactNode }) {
  const { value: selectedValue, onValueChange } = useSelect()
  return (
    <div
      className={`px-3 py-2 text-sm cursor-pointer hover:bg-accent ${selectedValue === value ? 'bg-accent' : ''}`}
      onClick={() => onValueChange(value)}
    >
      {children}
    </div>
  )
}
