import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { prettyJSON } from 'hono/pretty-json'
import { showRoutes } from 'hono/dev';
import { subject } from './api/subject';
import { question } from './api/question';

export type Env = {
  DB: D1Database;
  BUCKET: R2Bucket;
  CACHE: KVNamespace;
  ENV_TYPE: 'dev' | 'prod' | 'stage';
};

const app = new Hono<{ Bindings: Env }>();

app.use(prettyJSON())
app.use('/v1/*',
  cors({
    origin: (origin) => origin,
    allowMethods: ['POST', 'PUT', 'DELETE', 'GET', 'OPTIONS'],
    exposeHeaders: ['Content-Length', 'X-Kuma-Revision'],
    allowHeaders: ['Content-Type', 'Authorization', 'Accept', 'Accept-Language', 'Access-Control-Request-Headers', 'Access-Control-Request-Method', 'Cache-Control', 'Connection', 'Origin', 'Pragma', 'Referer', 'Sec-Fetch-Mode', 'User-Agent'],
    maxAge: 600,
    credentials: true,
  })
)

app.notFound((c) => c.json({ status: 404, msg: 'Not Found' }))
app.route('v1/subject', subject);
app.route('v1/question', question);

export default app;

app.get('/ping', (c) => {
  return c.text('pong');
});

showRoutes(app, { verbose: true })
