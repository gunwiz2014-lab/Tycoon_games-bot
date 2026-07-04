```javascript
const { Telegraf, Markup } = require('telegraf');

// Токен бота и ссылка для платежей от @BotFather
const BOT_TOKEN = process.env.BOT_TOKEN || 'YOUR_BOT_TOKEN_HERE';
const bot = new Telegraf(BOT_TOKEN);

// Игровая база данных в памяти (хранит состояние игроков по их telegram ID)
const db = {};

// Функция для получения или инициализации профиля пользователя
function getProfile(userId, firstName) {
  if (!db[userId]) {
    db[userId] = {
      userId,
      name: firstName,
      money: 1000,        // Игровые доллары ($)
      energy: 150,        // Энергия
      maxEnergy: 150,
      
      // VIP и Бусты
      isVip: false,
      hasAutoClicker: false,
      doubleYield: false,

      // Завод лимонов
      lemons: 0,
      juice: 0,
      lemonPressLvl: 1,
      autoSqueezerLvl: 0,
      plantationLvl: 0,

      // Шахта
      coal: 0,
      gold: 0,
      diamonds: 0,
      pickaxeLvl: 1,
      mineDrills: 0,

      // Майнинг
      ton: 0,
      gpuRigCount: 0,
      asicCount: 0,

      lastUpdate: Date.now()
    };
  }
  return db[userId];
}

// Фоновое обновление пассивного дохода и энергии (ленивое, при каждом запросе пользователя)
function updatePassiveIncome(profile) {
  const now = Date.now();
  const diffSec = Math.floor((now - profile.lastUpdate) / 1000);
  
  if (diffSec <= 0) return;

  // 1. Пассивное производство завода
  const lemonIncome = profile.plantationLvl * 3 * diffSec;
  const juiceIncome = profile.autoSqueezerLvl * 0.6 * diffSec;
  profile.lemons += lemonIncome;
  profile.juice += juiceIncome;

  // 2. Пассивная добыча в шахте
  const coalIncome = profile.mineDrills * 2 * diffSec;
  profile.coal += coalIncome;
  // Золото и алмазы добываются с шансом при пассивной работе буров
  if (profile.mineDrills > 0) {
    const goldChance = 0.3 * profile.mineDrills * diffSec;
    const diamondChance = 0.05 * profile.mineDrills * diffSec;
    profile.gold += Math.floor(goldChance);
    profile.diamonds += Math.floor(diamondChance);
  }

  // 3. Пассивный майнинг TON
  const tonIncome = (profile.gpuRigCount * 0.004 + profile.asicCount * 0.025) * diffSec;
  profile.ton = parseFloat((profile.ton + tonIncome).toFixed(4));

  // 4. Регенерация энергии
  const regenRate = profile.isVip ? 5 : 2; // Энергии в секунду
  profile.energy = Math.min(profile.maxEnergy, profile.energy + (regenRate * diffSec));

  profile.lastUpdate = now;
}

// Цены на рынке (меняются глобально при запросах)
let marketPrices = {
  lemon: 1.5,
  juice: 5.0,
  coal: 3.2,
  gold: 25.0,
  diamond: 120.0,
  ton: 7.2
};

function randomizeMarket() {
  if (Math.random() < 0.3) {
    marketPrices = {
      lemon: Math.max(0.6, parseFloat((marketPrices.lemon + (Math.random() * 0.4 - 0.2)).toFixed(2))),
      juice: Math.max(2.5, parseFloat((marketPrices.juice + (Math.random() * 1.2 - 0.6)).toFixed(2))),
      coal: Math.max(1.5, parseFloat((marketPrices.coal + (Math.random() * 0.8 - 0.4)).toFixed(2))),
      gold: Math.max(12.0, parseFloat((marketPrices.gold + (Math.random() * 5.0 - 2.5)).toFixed(2))),
      diamond: Math.max(60.0, parseFloat((marketPrices.diamond + (Math.random() * 15.0 - 7.5)).toFixed(2))),
      ton: Math.max(4.0, parseFloat((marketPrices.ton + (Math.random() * 1.5 - 0.75)).toFixed(2)))
    };
  }
}

// === КНОПКИ ГЛАВНОГО МЕНЮ ===
const mainMenuKeyboard = () => {
  return Markup.keyboard([
    ['🍋 Завод', '⛏️ Шахта', '🖥️ Майнинг-Ферма'],
    ['🏪 Лавочка (Рынок)', '👑 VIP & Магазин Stars'],
    ['📊 Мой Профиль', '🔄 Обновить Баланс']
  ]).resize();
};

// === КОМАНДА /START ===
bot.start((ctx) => {
  const profile = getProfile(ctx.from.id, ctx.from.first_name);
  ctx.replyWithMarkdownV2(
    `👋 *Привет, ${ctx.from.first_name || 'Игрок'}\\!* Добро пожаловать в текстовый симулятор *Multi\\-Tycoon \\& Miner*\\!\n\n` +
    `Здесь ты можешь построить огромную империю прямо в чате Telegram:\n` +
    `🍋 *Выжимай лимоны* и делай сок на Лимонном Заводе\\!\n` +
    `⛏️ *Копай глубокие шахты* в поисках алмазов и золота\\!\n` +
    `🖥️ *Запускай майнинг\\-фермы* и пассивно добывай крипту TON\\!\n` +
    `⭐️ *Покупай уникальные улучшения* за Telegram Stars\\!\n\n` +
    `Используй кнопки ниже для управления своей корпорацией\\!`,
    mainMenuKeyboard()
  );
});

// === ОБРАБОТЧИК: ПРОФИЛЬ ===
bot.hears(['📊 Мой Профиль', '🔄 Обновить Баланс'], (ctx) => {
  const profile = getProfile(ctx.from.id, ctx.from.first_name);
  updatePassiveIncome(profile);
  randomizeMarket();

  const text = `📊 *Игровой Профиль: ${profile.name}*\n\n` +
    `💵 *Баланс:* $${profile.money.toLocaleString()}\n` +
    `⚡ *Энергия:* ${Math.floor(profile.energy)} / ${profile.maxEnergy}\n` +
    `👑 *VIP Статус:* ${profile.isVip ? '✅ Активен (x2 клик, x2 энергия)' : '❌ Нет'}\n\n` +
    `🍋 *Склад Завода:* 🍋 ${profile.lemons} шт. | 🥤 ${profile.juice.toFixed(1)}л сока\n` +
    `⛏️ *Склад Шахты:* 🪨 ${profile.coal} угля | 🪙 ${profile.gold} золота | 💎 ${profile.diamonds} алмазов\n` +
    `💎 *Кошелек:* ${profile.ton.toFixed(4)} TON\n\n` +
    `_Пассивный доход обновлен автоматически!_`;

  ctx.replyWithMarkdown(text, mainMenuKeyboard());
});

// === ОБРАБОТЧИК: ЗАВОД ===
bot.hears('🍋 Завод', (ctx) => {
  const profile = getProfile(ctx.from.id, ctx.from.first_name);
  updatePassiveIncome(profile);

  const clickPower = profile.lemonPressLvl * (profile.doubleYield ? 2 : 1) * (profile.isVip ? 2 : 1);
  const pressCost = Math.round(60 * Math.pow(1.5, profile.lemonPressLvl));
  const squezerCost = Math.round(200 * Math.pow(1.6, profile.autoSqueezerLvl));
  const plantationCost = Math.round(2500 * Math.pow(1.8, profile.plantationLvl));

  const text = `🍋 *Лимонный Завод Тайкун*\n\n` +
    `🍋 Лимонов на складе: *${profile.lemons} шт.*\n` +
    `🥤 Сока выжато: *${profile.juice.toFixed(1)} л*\n\n` +
    `⚙️ *Твои улучшения:* \n` +
    `• Ручной Пресс: Уровень *${profile.lemonPressLvl}* (+${clickPower} 🍋 за клик)\n` +
    `• Авто-выжималка: Уровень *${profile.autoSqueezerLvl}* (+${(profile.autoSqueezerLvl * 0.6).toFixed(1)}л сока/сек)\n` +
    `• Лимонная Роща: Уровень *${profile.plantationLvl}* (+${profile.plantationLvl * 3} 🍋/сек пассивно)\n\n` +
    `🔋 _Каждое ручное выжимание тратит 1 энергию._`;

  const inlineKeyboard = Markup.inlineKeyboard([
    [Markup.button.callback('🍋 Выжать Лимон (Ручной Клик)', 'click_lemon')],
    [Markup.button.callback(`⚙️ Прокачать Пресс ($${pressCost})`, 'up_press')],
    [Markup.button.callback(`🥤 Купить Авто-выжималку ($${squezerCost})`, 'up_squeezer')],
    [Markup.button.callback(`🌳 Купить Лимонную Рощу ($${plantationCost})`, 'up_plantation')]
  ]);

  ctx.replyWithMarkdown(text, inlineKeyboard);
});

// === ОБРАБОТЧИК: ШАХТА ===
bot.hears('⛏️ Шахта', (ctx) => {
  const profile = getProfile(ctx.from.id, ctx.from.first_name);
  updatePassiveIncome(profile);

  const pickCost = Math.round(100 * Math.pow(1.6, profile.pickaxeLvl));
  const drillCost = Math.round(450 * Math.pow(1.7, profile.mineDrills));

  const text = `⛏️ *Угольно-Алмазная Шахта*\n\n` +
    `🪨 Уголь: *${profile.coal}*\n` +
    `🪙 Золотая руда: *${profile.gold}*\n` +
    `💎 Чистые алмазы: *${profile.diamonds}*\n\n` +
    `⚙️ *Оборудование:* \n` +
    `• Стальная кирка: Уровень *${profile.pickaxeLvl}*\n` +
    `• Буровые установки: *${profile.mineDrills} шт.* (+${profile.mineDrills * 2} угля/сек пассивно)\n\n` +
    `🔋 _Ручная добыча тратит 2 энергии._`;

  const inlineKeyboard = Markup.inlineKeyboard([
    [Markup.button.callback('⛏️ Копать Руду (Ручной Клик)', 'click_mine')],
    [Markup.button.callback(`⚙️ Прокачать Кирку ($${pickCost})`, 'up_pickaxe')],
    [Markup.button.callback(`🚜 Купить Буровую Установку ($${drillCost})`, 'up_drill')]
  ]);

  ctx.replyWithMarkdown(text, inlineKeyboard);
});

// === ОБРАБОТЧИК: МАЙНИНГ ===
bot.hears('🖥️ Майнинг-Ферма', (ctx) => {
  const profile = getProfile(ctx.from.id, ctx.from.first_name);
  updatePassiveIncome(profile);

  const gpuCost = Math.round(500 * Math.pow(1.5, profile.gpuRigCount));
  const asicCost = Math.round(2200 * Math.pow(1.6, profile.asicCount));
  const currentIncome = profile.gpuRigCount * 0.004 + profile.asicCount * 0.025;

  const text = `🖥️ *Крипто-Майнинг Ферма*\n\n` +
    `💎 Твой баланс: *${profile.ton.toFixed(4)} TON*\n` +
    `⚡ Пассивный доход: *+${currentIncome.toFixed(3)} TON/сек*\n\n` +
    `🖥️ *Твое оборудование:* \n` +
    `• Фермы RTX 5090: *${profile.gpuRigCount} шт.* (+0.004 TON/сек)\n` +
    `• Промышленные ASIC: *${profile.asicCount} шт.* (+0.025 TON/сек)\n\n` +
    `Продавай накопленные TON в лавочке за доллары $!`;

  const inlineKeyboard = Markup.inlineKeyboard([
    [Markup.button.callback(`📟 Купить RTX 5090 ($${gpuCost})`, 'buy_gpu')],
    [Markup.button.callback(`🎛️ Купить ASIC ($${asicCost})`, 'buy_asic')]
  ]);

  ctx.replyWithMarkdown(text, inlineKeyboard);
});

// === ОБРАБОТЧИК: ЛАВОЧКА ===
bot.hears('🏪 Лавочка (Рынок)', (ctx) => {
  const profile = getProfile(ctx.from.id, ctx.from.first_name);
  updatePassiveIncome(profile);
  randomizeMarket();

  const text = `🏪 *Рыночная Лавочка Торговца*\n\n` +
    `Здесь ты можешь продать накопленное сырье. Цены меняются случайным образом!\n\n` +
    `📈 *Текущие цены покупки:* \n` +
    `🍋 Лимон: *$${marketPrices.lemon}* (У тебя: ${profile.lemons})\n` +
    `🥤 Сок (за литр): *$${marketPrices.juice}* (У тебя: ${profile.juice.toFixed(1)}л)\n` +
    `🪨 Уголь: *$${marketPrices.coal}* (У тебя: ${profile.coal})\n` +
    `🪙 Золото: *$${marketPrices.gold}* (У тебя: ${profile.gold})\n` +
    `💎 Алмаз: *$${marketPrices.diamond}* (У тебя: ${profile.diamonds})\n` +
    `💎 Валюта TON: *$${marketPrices.ton}* (У тебя: ${profile.ton.toFixed(2)} TON)`;

  const inlineKeyboard = Markup.inlineKeyboard([
    [Markup.button.callback('🍋 Продать Все Лимоны', 'sell_lemons'), Markup.button.callback('🥤 Продать Весь Сок', 'sell_juice')],
    [Markup.button.callback('🪨 Продать Весь Уголь', 'sell_coal'), Markup.button.callback('🪙 Продать Все Золото', 'sell_gold')],
    [Markup.button.callback('💎 Продать Все Алмазы', 'sell_diamonds'), Markup.button.callback('💎 Продать Весь TON', 'sell_ton')]
  ]);

  ctx.replyWithMarkdown(text, inlineKeyboard);
});

// === ОБРАБОТЧИК: VIP И ТЕЛЕГРАМ СТАРС ===
bot.hears('👑 VIP & Магазин Stars', (ctx) => {
  const profile = getProfile(ctx.from.id, ctx.from.first_name);
  updatePassiveIncome(profile);

  const text = `👑 *Магазин Telegram Stars* ⭐️\n\n` +
    `Приобретайте уникальные преимущества за официальные звёзды Telegram! Нажмите на любой товар, чтобы получить инвойс на оплату.\n\n` +
    `✨ *Доступные предложения:* \n` +
    `• *Императорский VIP-статус* (150 ⭐️)\n` +
    `  _Дает постоянный x2 к сбору лимонов, x2 к регенерации энергии!_\n` +
    `• *Золотой Урожай* (120 ⭐️)\n` +
    `  _Удваивает количество собираемых лимонов навсегда!_\n` +
    `• *Стартовый Капитал $15,000* (200 ⭐️)\n` +
    `  _Моментально начисляет 15,000 наличных игровых долларов._`;

  const inlineKeyboard = Markup.inlineKeyboard([
    [Markup.button.callback('👑 Купить VIP за 150 ⭐️', 'pay_vip')],
    [Markup.button.callback('🍋 Купить Золотой Урожай за 120 ⭐️', 'pay_harvest')],
    [Markup.button.callback('💵 Купить $15,000 за 200 ⭐️', 'pay_cash')]
  ]);

  ctx.replyWithMarkdown(text, inlineKeyboard);
});

// === OБРАБОТЧИКИ ИНЛАЙН-КНОПОК (CALLBACK QUERIES) ===
bot.on('callback_query', async (ctx) => {
  const userId = ctx.from.id;
  const profile = getProfile(userId, ctx.from.first_name);
  updatePassiveIncome(profile);
  const data = ctx.callbackQuery.data;

  try {
    // 1. Кликерские действия
    if (data === 'click_lemon') {
      if (profile.energy < 1) {
        return ctx.answerCbQuery('❌ Недостаточно энергии! Подождите восстановления.', { show_alert: true });
      }
      profile.energy -= 1;
      const amount = profile.lemonPressLvl * (profile.doubleYield ? 2 : 1) * (profile.isVip ? 2 : 1);
      profile.lemons += amount;
      ctx.answerCbQuery(`🍋 +${amount} лимонов!`);
      // Обновляем текст в чате
      return ctx.editMessageText(
        `🍋 *Вы выжали лимоны!*\nУ вас на складе: ${profile.lemons} 🍋`,
        {
          parse_mode: 'Markdown',
          reply_markup: Markup.inlineKeyboard([[Markup.button.callback('🍋 Выжать еще раз!', 'click_lemon')]])
        }
      );
    }

    if (data === 'click_mine') {
      if (profile.energy < 2) {
        return ctx.answerCbQuery('❌ Нужно минимум 2 энергии!', { show_alert: true });
      }
      profile.energy -= 2;
      const mult = profile.pickaxeLvl * (profile.isVip ? 2 : 1);
      const coalGain = Math.round((Math.random() * 3 + 1) * mult);
      profile.coal += coalGain;

      let extra = '';
      if (Math.random() < 0.35) {
        const goldGain = Math.round((Math.random() * 1 + 1) * mult);
        profile.gold += goldGain;
        extra += ` | +${goldGain} 🪙`;
      }
      if (Math.random() < 0.1) {
        profile.diamonds += 1;
        extra += ` | +1 💎`;
      }

      ctx.answerCbQuery(`⛏️ Добыто: +${coalGain} 🪨${extra}`);
      return ctx.editMessageText(
        `⛏️ *Вы покопали в шахте!*\nУголь: ${profile.coal} | Золото: ${profile.gold} | Алмазы: ${profile.diamonds}`,
        {
          parse_mode: 'Markdown',
          reply_markup: Markup.inlineKeyboard([[Markup.button.callback('⛏️ Копать еще раз!', 'click_mine')]])
        }
      );
    }

    // 2. Покупка улучшений завода
    if (data === 'up_press') {
      const cost = Math.round(60 * Math.pow(1.5, profile.lemonPressLvl));
      if (profile.money >= cost) {
        profile.money -= cost;
        profile.lemonPressLvl += 1;
        ctx.answerCbQuery('✅ Пресс успешно улучшен!');
      } else {
        ctx.answerCbQuery('❌ Недостаточно игровых долларов $!', { show_alert: true });
      }
    }

    if (data === 'up_squeezer') {
      const cost = Math.round(200 * Math.pow(1.6, profile.autoSqueezerLvl));
      if (profile.money >= cost) {
        profile.money -= cost;
        profile.autoSqueezerLvl += 1;
        ctx.answerCbQuery('✅ Авто-выжималка куплена!');
      } else {
        ctx.answerCbQuery('❌ Недостаточно игровых долларов $!', { show_alert: true });
      }
    }

    if (data === 'up_plantation') {
      const cost = Math.round(2500 * Math.pow(1.8, profile.plantationLvl));
      if (profile.money >= cost) {
        profile.money -= cost;
        profile.plantationLvl += 1;
        ctx.answerCbQuery('✅ Лимонная роща расширена!');
      } else {
        ctx.answerCbQuery('❌ Недостаточно игровых долларов $!', { show_alert: true });
      }
    }

    // 3. Улучшения шахты
    if (data === 'up_pickaxe') {
      const cost = Math.round(100 * Math.pow(1.6, profile.pickaxeLvl));
      if (profile.money >= cost) {
        profile.money -= cost;
        profile.pickaxeLvl += 1;
        ctx.answerCbQuery('✅ Кирка успешно улучшена!');
      } else {
        ctx.answerCbQuery('❌ Недостаточно $!', { show_alert: true });
      }
    }

    if (data === 'up_drill') {
      const cost = Math.round(450 * Math.pow(1.7, profile.mineDrills));
      if (profile.money >= cost) {
        profile.money -= cost;
        profile.mineDrills += 1;
        ctx.answerCbQuery('✅ Бур успешно запущен!');
      } else {
        ctx.answerCbQuery('❌ Недостаточно $!', { show_alert: true });
      }
    }

    // 4. Покупки майнинга
    if (data === 'buy_gpu') {
      const cost = Math.round(500 * Math.pow(1.5, profile.gpuRigCount));
      if (profile.money >= cost) {
        profile.money -= cost;
        profile.gpuRigCount += 1;
        ctx.answerCbQuery('✅ Видеокарта RTX 5090 добавлена!');
      } else {
        ctx.answerCbQuery('❌ Недостаточно $!', { show_alert: true });
      }
    }

    if (data === 'buy_asic') {
      const cost = Math.round(2200 * Math.pow(1.6, profile.asicCount));
      if (profile.money >= cost) {
        profile.money -= cost;
        profile.asicCount += 1;
        ctx.answerCbQuery('✅ Промышленный ASIC подключен!');
      } else {
        ctx.answerCbQuery('❌ Недостаточно $!', { show_alert: true });
      }
    }

    // 5. Продажа ресурсов
    if (data === 'sell_lemons') {
      if (profile.lemons <= 0) return ctx.answerCbQuery('❌ У вас нет лимонов!');
      const income = parseFloat((profile.lemons * marketPrices.lemon).toFixed(2));
      profile.money += income;
      ctx.answerCbQuery(`🍋 Продано ${profile.lemons} лимонов за $${income}`);
      profile.lemons = 0;
    }

    if (data === 'sell_juice') {
      if (profile.juice <= 0) return ctx.answerCbQuery('❌ У вас нет сока!');
      const income = parseFloat((profile.juice * marketPrices.juice).toFixed(2));
      profile.money += income;
      ctx.answerCbQuery(`🥤 Продано ${profile.juice.toFixed(1)}л сока за $${income}`);
      profile.juice = 0;
    }

    if (data === 'sell_coal') {
      if (profile.coal <= 0) return ctx.answerCbQuery('❌ У вас нет угля!');
      const income = parseFloat((profile.coal * marketPrices.coal).toFixed(2));
      profile.money += income;
      ctx.answerCbQuery(`🪨 Продано ${profile.coal} угля за $${income}`);
      profile.coal = 0;
    }

    if (data === 'sell_gold') {
      if (profile.gold <= 0) return ctx.answerCbQuery('❌ У вас нет золота!');
      const income = parseFloat((profile.gold * marketPrices.gold).toFixed(2));
      profile.money += income;
      ctx.answerCbQuery(`🪙 Продано ${profile.gold} золота за $${income}`);
      profile.gold = 0;
    }

    if (data === 'sell_diamonds') {
      if (profile.diamonds <= 0) return ctx.answerCbQuery('❌ У вас нет алмазов!');
      const income = parseFloat((profile.diamonds * marketPrices.diamond).toFixed(2));
      profile.money += income;
      ctx.answerCbQuery(`💎 Продано ${profile.diamonds} алмазов за $${income}`);
      profile.diamonds = 0;
    }

    if (data === 'sell_ton') {
      if (profile.ton <= 0) return ctx.answerCbQuery('❌ У вас нет TON!');
      const income = parseFloat((profile.ton * marketPrices.ton).toFixed(2));
      profile.money += income;
      ctx.answerCbQuery(`💎 Продано ${profile.ton.toFixed(4)} TON за $${income}`);
      profile.ton = 0;
    }

    // 6. Выставление счета (Telegram Stars)
    if (data === 'pay_vip') {
      await ctx.answerCbQuery('Создаем счет на оплату VIP...');
      return await sendStarsInvoice(ctx, 'Императорский VIP', 'Удвоенный сбор лимонов и регенерация энергии навсегда', 'vip', 150);
    }
    if (data === 'pay_harvest') {
      await ctx.answerCbQuery('Создаем счет...');
      return await sendStarsInvoice(ctx, 'Золотой Урожай', 'Постоянный множитель x2 на сбор лимонов', 'double', 120);
    }
    if (data === 'pay_cash') {
      await ctx.answerCbQuery('Создаем счет...');
      return await sendStarsInvoice(ctx, 'Стартовый капитал $15,000', 'Мгновенное начисление игровых долларов', 'cash', 200);
    }

  } catch (error) {
    console.error('Callback error:', error);
  }
});

// Функция отправки инвойса на оплату Stars
async function sendStarsInvoice(ctx, title, description, payloadId, priceStars) {
  try {
    await ctx.replyWithInvoice(
      title,
      description,
      JSON.stringify({ userId: ctx.from.id, itemId: payloadId }),
      '', // Для Telegram Stars провайдер токен ВСЕГДА пустой
      'XTR', // Валюта Stars
      [{ label: title, amount: priceStars }]
    );
  } catch (e) {
    console.error('Invoice creation failed', e);
    await ctx.reply('❌ Не удалось выставить счет. Проверьте настройки оплаты в Telegram.');
  }
}

// Проверка платежа перед списанием
bot.on('pre_checkout_query', async (ctx) => {
  try {
    await ctx.answerPreCheckoutQuery(true);
  } catch (e) {
    console.error('Precheckout error', e);
  }
});

// Успешный платеж
bot.on('successful_payment', async (ctx) => {
  const payment = ctx.message.successful_payment;
  const payload = JSON.parse(payment.invoice_payload);
  const profile = getProfile(payload.userId, ctx.from.first_name);

  if (payload.itemId === 'vip') {
    profile.isVip = true;
  } else if (payload.itemId === 'double') {
    profile.doubleYield = true;
  } else if (payload.itemId === 'cash') {
    profile.money += 15000;
  }

  await ctx.reply(`🎉 Спасибо за покупку! Вы успешно приобрели услугу за ${payment.total_amount} ⭐️. Изменения применились к вашему аккаунту!`);
});

// Запуск бота на Railway
const PORT = process.env.PORT || 3000;
bot.launch().then(() => {
  console.log('Telegram Text-Tycoon Bot successfully running!');
});

// Плавное выключение
process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));

```
