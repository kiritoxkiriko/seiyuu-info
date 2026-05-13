import type { Actor, ActorDetail, EventItem, Language, SnsPost } from "../types";

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
    bio: "奈良县出身，青二プロダクション所属。特长是舞蹈和关西腔。代表角色包括《我心里危险的东西》山田杏奈、《BanG Dream! It's MyGO!!!!!》高松燈。",
    profile_url: "https://www.aoni.co.jp/search/yomiya-hina.html",
    officialPhoto: {
      url: "https://pbs.twimg.com/media/HH3p_P3asAA0MX2?format=jpg&name=large",
      alt: "羊宮妃那 X 投稿写真",
      source: "X / Hina_Youmiya",
    },
    gallery: [
      {
        url: "https://pbs.twimg.com/media/HH3p_P3asAA0MX2?format=jpg&name=large",
        alt: "羊宮妃那 X 投稿写真",
        source: "X / Hina_Youmiya",
      },
    ],
    specialties: ["舞蹈", "关西腔"],
    hobbies: ["绘画", "阅读", "电影鉴赏", "音乐鉴赏", "作词", "作曲"],
    roles: [
      { title: "我心里危险的东西", character: "山田杏奈" },
      { title: "BanG Dream! It's MyGO!!!!!", character: "高松燈" },
    ],
    socialLinks: [
      { platform: "x", label: "X", url: "https://x.com/Hina_Youmiya" },
      { platform: "website", label: "青二プロフィール", url: "https://www.aoni.co.jp/search/yomiya-hina.html" },
    ],
  },
  {
    id: "aoki-hina",
    name: "青木陽菜",
    kana: "あおき ひな",
    romanized: "Hina Aoki",
    agency: "響",
    birthday: "1月5日",
    birthplace: "宮城県",
    bio: "宫城县出身，響所属。特长是钢琴和歌唱。代表角色包括《BanG Dream! It's MyGO!!!!!》要楽奈、《カードファイト!! ヴァンガード will+Dress Season2》ハロナ・ウォーカー。",
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
    specialties: ["钢琴", "歌唱"],
    hobbies: ["吉他", "弹唱", "一个人唱卡拉 OK", "观看演唱会"],
    roles: [{ title: "BanG Dream! It's MyGO!!!!!", character: "要楽奈" }],
    socialLinks: [
      { platform: "x", label: "X", url: "https://x.com/aoki__hina" },
      { platform: "instagram", label: "Instagram", url: "https://www.instagram.com/aoki_hina_official/" },
    ],
  },
  {
    id: "hayashi-coco",
    name: "林鼓子",
    kana: "はやし ここ",
    romanized: "Coco Hayashi",
    agency: "LIBERTE",
    birthday: "5月15日",
    birthplace: "静岡県",
    bio: "静冈县出身，LIBERTE 所属。擅长鼓、打击乐和钢琴。代表角色包括《BanG Dream! It's MyGO!!!!!》椎名立希、《ラブライブ！虹ヶ咲学園スクールアイドル同好会》優木せつ菜。",
    profile_url: "https://fan.pia.jp/cocohayashi/",
    officialPhoto: {
      url: "https://pbs.twimg.com/media/HHEg5WhboAAZWTt?format=jpg&name=large",
      alt: "林鼓子 X 投稿写真",
      source: "X / cocohayashi515",
    },
    gallery: [
      {
        url: "https://pbs.twimg.com/media/HHEg5WhboAAZWTt?format=jpg&name=large",
        alt: "林鼓子 X 投稿写真",
        source: "X / cocohayashi515",
      },
    ],
    specialties: ["架子鼓", "打击乐", "钢琴"],
    hobbies: ["音乐剧鉴赏", "画插画"],
    roles: [
      { title: "BanG Dream! It's MyGO!!!!!", character: "椎名立希" },
      { title: "Love Live! 虹咲学园学园偶像同好会", character: "优木雪菜 / 中川菜菜" },
      { title: "美妙频道", character: "桃山未来" },
    ],
    socialLinks: [
      { platform: "x", label: "X", url: "https://x.com/cocohayashi515" },
      { platform: "instagram", label: "Instagram", url: "https://www.instagram.com/coco_hayashi.official/" },
      { platform: "website", label: "Official Site", url: "https://fan.pia.jp/cocohayashi/" },
    ],
    eventernoteUrl: "https://www.eventernote.com/actors/%E6%9E%97%E9%BC%93%E5%AD%90/30284/events",
  },
  {
    id: "rina-togetoge",
    name: "理名",
    kana: "りな",
    romanized: "Rina",
    agency: "トゲナシトゲアリ / agehasprings",
    birthday: "11月13日",
    birthplace: "広島県",
    bio: "广岛县出身，トゲナシトゲアリ Vo.。在《ガールズバンドクライ》中担任井芹仁菜役，同时作为乐队主唱展开音乐活动。",
    profile_url: "https://www.universal-music.co.jp/togenashitogeari/biography/",
    officialPhoto: {
      url: "https://www.universal-music.co.jp/togenashitogeari/wp-content/uploads/sites/3991/2023/07/rina_main-683x1024.jpg",
      alt: "理名 アーティスト写真",
      source: "UNIVERSAL MUSIC JAPAN",
    },
    gallery: [
      {
        url: "https://www.universal-music.co.jp/togenashitogeari/wp-content/uploads/sites/3991/2023/07/rina_main-683x1024.jpg",
        alt: "理名 アーティスト写真",
        source: "UNIVERSAL MUSIC JAPAN",
      },
    ],
    specialties: ["睡眠"],
    hobbies: ["绘画"],
    roles: [{ title: "Girls Band Cry", character: "井芹仁菜" }],
    socialLinks: [
      { platform: "x", label: "X", url: "https://x.com/rina_togetoge" },
      { platform: "instagram", label: "Instagram", url: "https://www.instagram.com/rina_togetoge/" },
      { platform: "website", label: "トゲナシトゲアリ Biography", url: "https://www.universal-music.co.jp/togenashitogeari/biography/" },
    ],
    eventernoteUrl: "https://www.eventernote.com/actors/%E7%90%86%E5%90%8D/73862/events",
  },
  {
    id: "kusunoki-tomori",
    name: "楠木ともり",
    kana: "くすのき ともり",
    romanized: "Tomori Kusunoki",
    agency: "Sony Music Artists",
    birthday: "12月22日",
    birthplace: "東京都",
    bio: "东京都出身，Sony Music Artists 所属。声优兼创作歌手。代表角色包括《チェンソーマン》マキマ、《ソードアート・オンライン オルタナティブ ガンゲイル・オンライン》レン、《プロジェクトセカイ》宵崎奏。",
    profile_url: "https://www.sma.co.jp/s/sma/artist/441",
    officialPhoto: {
      url: "https://www.sma.co.jp/s/sma/artist_photo/441",
      alt: "楠木ともり 公式プロフィール写真",
      source: "Sony Music Artists",
    },
    gallery: [
      {
        url: "https://www.sma.co.jp/s/sma/artist_photo/441",
        alt: "楠木ともり 公式プロフィール写真",
        source: "Sony Music Artists",
      },
    ],
    specialties: ["绘画", "小号"],
    hobbies: ["作词作曲", "演奏和听音乐", "逛画材店", "游戏", "上网"],
    roles: [
      { title: "链锯人", character: "玛奇玛" },
      { title: "刀剑神域外传 Gun Gale Online", character: "莲 / 小比类卷香莲" },
      { title: "世界计划 缤纷舞台！feat. 初音未来", character: "宵崎奏" },
      { title: "绯染天空", character: "茅森月歌" },
    ],
    socialLinks: [
      { platform: "x", label: "X", url: "https://x.com/tomori_kusunoki" },
      { platform: "website", label: "Official Website", url: "https://www.kusunokitomori.com/" },
      { platform: "website", label: "SMA Profile", url: "https://www.sma.co.jp/s/sma/artist/441" },
    ],
    eventernoteUrl: "https://www.eventernote.com/actors/%E6%A5%A0%E6%9C%A8%E3%81%A8%E3%82%82%E3%82%8A/27163/events",
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
    language: "original",
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
    language: "original",
  },
];

export const fallbackSns: SnsPost[] = [
  {
    id: "aoki-x-1",
    actorId: "aoki-hina",
    platform: "x",
    postedAt: "2026-05-07T10:00:00+09:00",
    text: "HiBiKi StYle+ 関連のお知らせを公開しました。",
    detailText: "HiBiKi StYle+ 関連のお知らせを公開しました。",
    url: "https://x.com/aoki__hina",
    kind: "original",
    mediaUrls: [],
    language: "original",
  },
  {
    id: "yomiya-x-1",
    actorId: "yomiya-hina",
    platform: "x",
    postedAt: "2026-04-11T09:00:00+09:00",
    text: "出演信息与近况更新。",
    detailText: "出演信息与近况更新。活动详情请结合置顶推文和官网一起查看。",
    url: "https://x.com/Hina_Youmiya",
    kind: "original",
    mediaUrls: [],
    language: "original",
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
  return getJson<Actor[]>("/api/v1/actors")
    .catch(() => fallbackActors)
    .then(sortActorsByRomanized);
}

export async function fetchActorDetail(actorId: string, language: Language): Promise<ActorDetail> {
  return getJson<ActorDetail>(`/api/v1/actors/${actorId}?event_source=eventernote&sns_source=x&language=${language}&cache=true`).catch(() => ({
    actor: fallbackActors.find((actor) => actor.id === actorId) ?? fallbackActors[0],
    events: fallbackEvents.filter((event) => event.actorId === actorId),
    sns: fallbackSns.filter((post) => post.actorId === actorId),
  }));
}

function sortActorsByRomanized(actors: Actor[]): Actor[] {
  return [...actors].sort((left, right) => left.romanized.localeCompare(right.romanized, "en", { sensitivity: "base" }));
}
