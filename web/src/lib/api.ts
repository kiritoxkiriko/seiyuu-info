import type { Actor, ActorDetail, EventItem, SnsPost } from "../types";

const API_BASE_URL = import.meta.env.PUBLIC_API_BASE_URL ?? "";

export const fallbackActors: Actor[] = [
  {
    id: "yomiya-hina",
    name: "羊宮妃那",
    kana: "ようみや ひな",
    romanized: "Hina Youmiya",
    agency: "青二プロダクション",
    birthday: "3月26日",
    birthplace: "奈良県",
    profile_url: "https://www.aoni.co.jp/search/yomiya-hina.html",
    officialPhoto: {
      url: "https://www.aoni.co.jp/search/items/yomiya-hina.jpg",
      alt: "羊宮妃那 公式プロフィール写真",
      source: "青二プロダクション",
    },
    gallery: [
      {
        url: "https://www.aoni.co.jp/search/items/yomiya-hina.jpg",
        alt: "羊宮妃那 宣材写真",
        source: "青二プロダクション",
      },
    ],
    specialties: ["ダンス", "関西弁"],
    hobbies: ["描画", "読書", "映画鑑賞", "音楽鑑賞", "作詞", "作曲"],
    roles: [
      { title: "僕の心のヤバいやつ", character: "山田杏奈" },
      { title: "BanG Dream! It's MyGO!!!!!", character: "高松燈" },
    ],
    socialLinks: [{ platform: "website", label: "青二プロフィール", url: "https://www.aoni.co.jp/search/yomiya-hina.html" }],
  },
  {
    id: "aoki-hina",
    name: "青木陽菜",
    kana: "あおき ひな",
    romanized: "Hina Aoki",
    agency: "響",
    birthday: "1月5日",
    birthplace: "宮城県",
    profile_url: "https://hibiki-cast.jp/hibiki_f/aoki_hina/",
    officialPhoto: {
      url: "https://bm-echoes.com/wordpress/wp-content/uploads/2024/07/17145908/hinaaoki_artistphoto_tate_FIX_resize-e1752732015470.jpg",
      alt: "青木陽菜 アーティスト写真",
      source: "BM-ECHOES",
    },
    gallery: [
      {
        url: "https://bm-echoes.com/wordpress/wp-content/uploads/2024/07/17145908/hinaaoki_artistphoto_tate_FIX_resize-e1752732015470.jpg",
        alt: "青木陽菜 アーティスト写真",
        source: "BM-ECHOES",
      },
    ],
    specialties: ["ピアノ", "歌"],
    hobbies: ["ギター", "弾き語り", "一人カラオケ", "ライブ鑑賞"],
    roles: [{ title: "BanG Dream! It's MyGO!!!!!", character: "要楽奈" }],
    socialLinks: [
      { platform: "x", label: "X", url: "https://x.com/aoki__hina" },
      { platform: "instagram", label: "Instagram", url: "https://www.instagram.com/aoki_hina_official/" },
    ],
  },
];

export const fallbackEvents: EventItem[] = [
  {
    id: "komorebi-yomiya",
    actorId: "yomiya-hina",
    title: "羊宮妃那のこもれびじかん",
    date: "2026-05-03",
    category: "broadcast",
    venue: "文化放送",
    url: "https://www.aoni.co.jp/search/yomiya-hina.html",
    source: "seed",
  },
  {
    id: "hibiki-style-omon-2026",
    actorId: "aoki-hina",
    title: "HiBiKi StYle+×王紋酒造 コラボ酒 関連企画",
    date: "2026-05-07",
    category: "release",
    venue: "Online",
    url: "https://hibikifan.com/aoki_hina",
    source: "seed",
  },
];

export const fallbackSns: SnsPost[] = [
  {
    id: "aoki-x-1",
    actorId: "aoki-hina",
    platform: "x",
    postedAt: "2026-05-07T10:00:00+09:00",
    text: "HiBiKi StYle+ 関連のお知らせを公開しました。",
    url: "https://x.com/aoki__hina",
    kind: "original",
    mediaUrls: [],
  },
  {
    id: "yomiya-web-1",
    actorId: "yomiya-hina",
    platform: "website",
    postedAt: "2026-04-11T09:00:00+09:00",
    text: "青二プロダクション公式プロフィールを更新。",
    url: "https://www.aoni.co.jp/search/yomiya-hina.html",
    kind: "original",
    mediaUrls: [],
  },
];

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export async function fetchActors(): Promise<Actor[]> {
  return getJson<Actor[]>("/api/v1/actors").catch(() => fallbackActors);
}

export async function fetchActorDetail(actorId: string): Promise<ActorDetail> {
  return getJson<ActorDetail>(`/api/v1/actors/${actorId}`).catch(() => ({
    actor: fallbackActors.find((actor) => actor.id === actorId) ?? fallbackActors[0],
    events: fallbackEvents.filter((event) => event.actorId === actorId),
    sns: fallbackSns.filter((post) => post.actorId === actorId),
  }));
}
