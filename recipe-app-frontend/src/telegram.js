export function initTelegram() {
    const tg = window.Telegram?.WebApp;
    if (!tg) return;
    tg.ready();
    tg.expand();
    tg.disableVerticalSwipes?.();
  }
  
  export function getInitData() {
    const fromTg = window.Telegram?.WebApp?.initData;
    if (fromTg) return fromTg;
    return import.meta.env.VITE_DEV_INIT_DATA || "";
  }
  
  export function haptic(type = "light") {
    window.Telegram?.WebApp?.HapticFeedback?.impactOccurred?.(type);
  }