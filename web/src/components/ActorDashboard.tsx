import { Activity, Sparkles } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { fetchActorDetail, fetchActors } from "../lib/api";
import type { Actor, ActorDetail, EventCategory, Language } from "../types";
import { ActorTabs, EventsPanel, Hero, LanguageSwitch, ProfileSummary, SnsPanel } from "./ActorSections";

export default function ActorDashboard() {
  const [actors, setActors] = useState<Actor[]>([]);
  const [activeId, setActiveId] = useState<string>("");
  const [detail, setDetail] = useState<ActorDetail | null>(null);
  const [category, setCategory] = useState<EventCategory | "all">("all");
  const [query, setQuery] = useState("");
  const [language, setLanguage] = useState<Language>("original");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchActors().then((items) => {
      setActors(items);
      setActiveId(items[0]?.id ?? "");
    });
  }, []);

  useEffect(() => {
    if (!activeId) {
      return;
    }
    setLoading(true);
    fetchActorDetail(activeId, language)
      .then(setDetail)
      .finally(() => setLoading(false));
  }, [activeId, language]);

  const filteredEvents = useMemo(() => {
    const events = detail?.events ?? [];
    return events.filter((event) => {
      const categoryMatched = category === "all" || event.category === category;
      const queryMatched = `${event.title} ${event.venue ?? ""}`.toLowerCase().includes(query.toLowerCase());
      return categoryMatched && queryMatched;
    });
  }, [category, detail?.events, query]);

  const actor = detail?.actor ?? actors[0];

  return (
    <main className="min-h-screen bg-paper text-ink">
      <Header actorCount={actors.length} />
      <section className="mx-auto grid max-w-7xl gap-5 px-4 py-6 sm:px-6 lg:grid-cols-[292px_minmax(0,1fr)] lg:px-8">
        <aside className="space-y-4">
          <ActorTabs actors={actors} activeId={activeId} onSelect={setActiveId} />
          {actor ? <ProfileSummary actor={actor} /> : null}
        </aside>

        {actor ? (
          <div className="space-y-6">
            <Hero actor={actor} loading={loading} />
            <LanguageSwitch language={language} onChange={setLanguage} />
            <div className="grid gap-6 xl:grid-cols-[minmax(0,1.08fr)_minmax(360px,0.92fr)]">
              <EventsPanel
                events={filteredEvents}
                category={category}
                query={query}
                onCategoryChange={setCategory}
                onQueryChange={setQuery}
              />
              <SnsPanel posts={detail?.sns ?? []} />
            </div>
          </div>
        ) : (
          <EmptyState />
        )}
      </section>
    </main>
  );
}

function Header({ actorCount }: { actorCount: number }) {
  return (
    <header className="border-b border-[#222938] bg-navy text-white">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-5 sm:px-6 lg:px-8">
        <div>
          <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.22em] text-[#98f0d4]">
            <Activity className="h-3.5 w-3.5" />
            voice actress intelligence
          </p>
          <h1 className="mt-1 text-3xl font-semibold tracking-normal sm:text-4xl">nsy 情报站</h1>
        </div>
        <div className="hidden items-center gap-2 rounded-md border border-white/[0.15] bg-white/[0.08] px-3 py-2 text-sm text-[#d7e2ea] sm:flex">
          <Sparkles className="h-4 w-4" />
          <span>{actorCount} 位配置中</span>
        </div>
      </div>
    </header>
  );
}

function EmptyState() {
  return <section className="border border-line bg-[#fbfaf7] p-8 text-sm text-moss">没有可用的声优配置。</section>;
}
