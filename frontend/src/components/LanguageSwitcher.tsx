import { useTranslation } from "react-i18next"
import { Languages } from "lucide-react"
import { SUPPORTED_LANGUAGES } from "../i18n"

const LABELS: Record<string, string> = { vi: "VI", zh: "中文", en: "EN" }

export default function LanguageSwitcher() {
  const { i18n, t } = useTranslation()
  const current = (SUPPORTED_LANGUAGES as readonly string[]).includes(i18n.language)
    ? i18n.language
    : "vi"

  return (
    <div className="flex items-center gap-2 px-3 py-2 text-sm text-muted-foreground">
      <Languages className="h-4 w-4" />
      <span className="sr-only">{t("common.language")}</span>
      <select
        value={current}
        onChange={e => i18n.changeLanguage(e.target.value)}
        className="bg-transparent outline-none font-medium cursor-pointer"
        aria-label={t("common.language")}
      >
        {SUPPORTED_LANGUAGES.map(lng => (
          <option key={lng} value={lng}>{LABELS[lng]}</option>
        ))}
      </select>
    </div>
  )
}
