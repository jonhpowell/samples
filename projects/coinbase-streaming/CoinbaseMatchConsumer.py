from datetime import datetime, timedelta
import faust

app = faust.App(
    'coinbase_matches',
    broker='kafka://localhost:9092',
    value_serializer='raw',
)


class Match(faust.Record, serializer='json', isodates=True):
    trade_id: int
    product_id: str
    price: float
    size: float
    time: datetime = None


class CandleStats(faust.Record, isodates=True):
    product_id: str = None
    start_time: datetime = None
    first_price: float = None
    last_price: float = None
    lowest_price: float = 1.0E6
    highest_price: float = -1.0E6
    total_amount: float = 0.0


coinbase_match_topic = app.topic('coinbase_matches', value_type=Match)

stats_1min = app.Table('stats_1_min', default=CandleStats, value_type=CandleStats)\
    .tumbling(timedelta(minutes=1), expires=timedelta(hours=1))\
    .relative_to_field(Match.time)


@app.agent(coinbase_match_topic)
async def coinbase_match(matches):
    async for match in matches.group_by(Match.product_id):
        product_id = match.product_id
        stats = stats_1min[product_id].current()
        if stats.product_id is None:
            stats.product_id = match.product_id
            stats.start_time = match.time
            stats.first_price = match.price
            stats.lowest_price = match.price
            stats.highest_price = match.price
            stats.total_amount = match.price
        else:
            stats.lowest_price = match.price if match.price < stats.lowest_price else stats.lowest_price
            stats.highest_price = match.price if match.price > stats.highest_price else stats.highest_price
        stats.last_price = match.price
        stats.total_amount += match.price
        print(stats)
        stats_1min[product_id] = stats

        #print(f'{product_id} dict: ${stats_1_min[product_id].current()}')


# use .delta() to get prior results in table

@app.page('/stats1min/{product_id}/')
@app.table_route(table=stats_1min, match_info='product_id')
async def get_stats1min(web, request, product_id):
    return web.json({
        product_id: stats_1min[product_id].now(),
    })



count = [0]


@app.page('/count/')
async def get_count(self, request):
    # update the counter
    count[0] += 1
    # and return it.
    return self.json({
        'count': count[0],
    })
