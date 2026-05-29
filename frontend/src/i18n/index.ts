import i18n from "i18next"
import { initReactI18next } from "react-i18next"
import LanguageDetector from "i18next-browser-languagedetector"
import vi from "./locales/vi.json"
import zh from "./locales/zh.json"
import en from "./locales/en.json"

export const SUPPORTED_LANGUAGES = ["vi", "zh", "en"] as const
export type Lang = (typeof SUPPORTED_LANGUAGES)[number]

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      vi: { translation: vi },
      zh: { translation: zh },
      en: { translation: en },
    },
    fallbackLng: "vi",
    supportedLngs: SUPPORTED_LANGUAGES as unknown as string[],
    interpolation: { escapeValue: false },
    detection: {
      order: ["localStorage", "navigator"],
      lookupLocalStorage: "i18nextLng",
      caches: ["localStorage"],
    },
  })

export default i18n
