import { Box, Sparkles, Zap, Brain, Info } from "lucide-react"
import { useTranslation } from "react-i18next"

export default function ModelsPage() {
  const { t } = useTranslation()

  const SUFFIXES = [
    { id: "-fast", icon: <Zap className="h-4 w-4 text-amber-500" />, desc: t("models.fastDesc") },
    { id: "-think", icon: <Brain className="h-4 w-4 text-blue-500" />, desc: t("models.thinkDesc") },
    { id: "-auto", icon: <Sparkles className="h-4 w-4 text-purple-500" />, desc: t("models.autoDesc") },
  ]

  const MODELS = [
    { id: "qwen3.7-max", base: "qwen3.7-max", tag: t("models.tagFlagship"), color: "emerald" },
    { id: "qwen-max", base: "qwen3.7-max", tag: t("models.tagAlias"), color: "slate" },
    { id: "qwen3.6-plus", base: "qwen3.6-plus", tag: t("models.tagMainstream"), color: "blue" },
    { id: "qwen-plus", base: "qwen3.6-plus", tag: t("models.tagAlias"), color: "slate" },
    { id: "qwen", base: "qwen3.6-plus", tag: t("models.tagAlias"), color: "slate" },
    { id: "qwen3.5-plus", base: "qwen3.5-plus", tag: t("models.tagLegacy"), color: "orange" },
    { id: "qwen3.5-flash", base: "qwen3.5-flash", tag: t("models.tagLegacy"), color: "orange" },
    { id: "qwen-turbo", base: "qwen3.5-flash", tag: t("models.tagAlias"), color: "slate" },
    { id: "deepseek-chat", base: "qwen3.6-plus", tag: "DS Alias", color: "slate" },
  ]

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      <div>
        <h2 className="text-3xl font-extrabold tracking-tight">{t("models.title")}</h2>
        <p className="text-muted-foreground mt-2">{t("models.subtitle")}</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Mode Suffixes Explanation */}
        <div className="rounded-2xl border bg-card/40 p-6 space-y-4 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary/10 rounded-lg">
              <Box className="h-5 w-5 text-primary" />
            </div>
            <h3 className="font-bold text-xl">{t("models.suffixTitle")}</h3>
          </div>
          <p className="text-sm text-muted-foreground">{t("models.suffixDesc")}</p>
          <div className="space-y-3 pt-2">
            {SUFFIXES.map(s => (
              <div key={s.id} className="flex items-center gap-4 p-3 rounded-xl bg-muted/30 border border-border/50">
                <code className="bg-primary/10 text-primary px-2 py-1 rounded font-bold text-sm min-w-[70px] text-center">
                  {s.id}
                </code>
                <div className="flex items-center gap-2 text-sm font-medium">
                  {s.icon}
                  {s.desc}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Example card */}
        <div className="rounded-2xl border border-blue-500/20 bg-blue-500/5 p-6 space-y-4 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-500/10 rounded-lg">
              <Info className="h-5 w-5 text-blue-500" />
            </div>
            <h3 className="font-bold text-xl">{t("models.exampleTitle")}</h3>
          </div>
          <div className="space-y-4 pt-2">
            <p className="text-sm text-muted-foreground">Ví dụ gọi API bằng Model ID tùy chỉnh:</p>
            <div className="bg-slate-950 p-4 rounded-xl font-mono text-xs text-slate-300 space-y-2">
              <p><span className="text-pink-500">"model"</span>: <span className="text-emerald-400">"qwen3.7-max-think"</span></p>
              <p className="text-slate-500">// {t("models.thinkDesc")}</p>
              <hr className="border-slate-800" />
              <p><span className="text-pink-500">"model"</span>: <span className="text-emerald-400">"qwen3.6-plus-fast"</span></p>
              <p className="text-slate-500">// {t("models.fastDesc")}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="rounded-2xl border bg-card/30 overflow-hidden shadow-xl">
        <table className="w-full text-sm text-left">
          <thead className="bg-muted/50 border-b text-muted-foreground text-xs uppercase tracking-wider font-semibold">
            <tr>
              <th className="h-12 px-6 align-middle">{t("models.colModel")}</th>
              <th className="h-12 px-6 align-middle">{t("models.colResolved")}</th>
              <th className="h-12 px-6 align-middle text-right">{t("models.colDesc")}</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/50">
            {MODELS.map(m => (
              <tr key={m.id} className="hover:bg-black/5 dark:hover:bg-white/5 transition-colors">
                <td className="px-6 py-4 align-middle font-bold font-mono text-foreground/90">{m.id}</td>
                <td className="px-6 py-4 align-middle font-mono text-xs text-muted-foreground">{m.base}</td>
                <td className="px-6 py-4 align-middle text-right">
                  <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-bold ring-1
                    ${m.color === 'emerald' ? 'bg-emerald-500/10 text-emerald-600 ring-emerald-500/20' :
                      m.color === 'blue' ? 'bg-blue-500/10 text-blue-600 ring-blue-500/20' :
                      m.color === 'orange' ? 'bg-orange-500/10 text-orange-600 ring-orange-500/20' :
                      'bg-slate-500/10 text-slate-600 ring-slate-500/20'}`}>
                    {m.tag}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
