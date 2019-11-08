#!/usr/bin/env python3
"""Case A6

У Игоря есть гипотеза, что одно из двух дополнительных действий
может вызывать целевое действие: то есть пользователи,
совершившие event_1 или event_2, с большей вероятностью совершат
и целевое действие. Нужно проверить, так ли это.

Другая задача — понять, какие именно пользователи
совершают целевые действия. Менеджер продукта выдвигает
гипотезу, что чаще всего по несколько раз фильмы/сериалы
покупают одни и те же пользователи, то есть небольшой
процент пользователей обеспечивает почти все действия,
приносящие нам прибыль."""

import pandas as pd

EVENTS_DICT = {
  'activation'  : 'activation',
  'registration': 'registration',
  'tarif_set'   : 'tarif_set',
  'event_1'     : 'Просмотр персональных рекомендаций',
  'event_2'     : 'Просмотр трейлера',
  'target_event': 'Покупка медиа',
}

# Загрузка исходных данных из JSON
df = pd.read_json("case6.json.gz", orient='records', convert_dates='created_at',
                  date_unit='ns', compression='gzip')

# Кол-во уникальных пользователей всего и тех из них, которые совершили целевое действие,
# плюс считаем конверсию.
users_count        = df.user_id.nunique()
users_target_count = df[df.event_type=='target_event'].user_id.nunique()
conversion         = users_target_count / users_count

# Частота разных событий
evts_df = pd.DataFrame(df.event_type.value_counts())
evts_df['evt_pct'] = evts_df.event_type * 100 / sum(evts_df.event_type)

# Строим таблицу по пользователям и событиям, которые эти пользователи сгенерировали.
users_events = df.loc[:,['user_id', 'event_type', 'created_at']].groupby(by=['user_id', 'event_type'], axis=0, as_index=True).count()

user_events2 = df.pivot_table(values='created_at', index='user_id', columns='event_type', aggfunc='count')
# Результат pivot_table выглядит привычнее, но удобнее ли будет по нему суммировать и искать закономерности?

# Получившуюся сводную таблицу можно проверить, расчитав, к примеру, конверсию:
assert(conversion == user_events2.target_event.count()/len(user_events2))

# Надо иметь в виду, что здесь не нужно суммировать, так как примерно 170 пользователей делали больше
# одной покупки (pt.target_event.value_counts())
# В таблице user_events2 колонки registration и tarif_set неинформативны, они содержат
# единицу для каждого пользователя (легко проверить value_counts), избавляюсь от них.

user_events2.drop(labels=['registration', 'tarif_set'], axis=1, inplace=True)

#
# Теперь смотрим, какие действия пользователя приводят к целевому действию.
# Например, активация совершенно необходима для всего остального:

