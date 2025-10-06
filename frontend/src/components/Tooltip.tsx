import React, { useState, type ReactNode } from "react";

type TooltipProps = {
  children: ReactNode;
  text: string;
  placement?: "top" | "right" | "bottom" | "left";
};

export default function Tooltip({ children, text, placement = "top" }: TooltipProps) {
  const [visible, setVisible] = useState(false);

  const show = () => setVisible(true);
  const hide = () => setVisible(false);

  const base = {
    position: "absolute" as const,
    zIndex: 50,
    padding: "6px 8px",
    background: "rgba(32,33,36,0.95)",
    color: "white",
    fontSize: 12,
    borderRadius: 6,
    whiteSpace: "nowrap" as const,
    pointerEvents: "none" as const,
    transformOrigin: "center",
    boxShadow: "0 4px 10px rgba(0,0,0,0.2)",
    opacity: visible ? 1 : 0,
    transition: "opacity 120ms ease",
  };

  const offsets: Record<string, React.CSSProperties> = {
    top: { left: "50%", bottom: "100%", transform: "translateX(-50%) translateY(-6px)" },
    right: { left: "100%", top: "50%", transform: "translateX(6px) translateY(-50%)" },
    bottom: { left: "50%", top: "100%", transform: "translateX(-50%) translateY(6px)" },
    left: { right: "100%", top: "50%", transform: "translateX(-6px) translateY(-50%)" },
  };

  return (
    <span
      style={{ position: "relative", display: "inline-flex", alignItems: "center" }}
      onMouseEnter={show}
      onMouseLeave={hide}
      onFocus={show}
      onBlur={hide}
    >
      {children}
      <span
        role="tooltip"
        aria-hidden={!visible}
        style={{ ...base, ...offsets[placement], pointerEvents: "none" }}
      >
        {text}
      </span>
    </span>
  );
}