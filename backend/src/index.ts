import { Hono } from 'hono';
import { prettyJSON } from 'hono/pretty-json'
import { showRoutes } from 'hono/dev';
import { subject } from './api/subject';

export type Env = {
  DB: D1Database;
  BUCKET: R2Bucket;
  CACHE: KVNamespace;
  ENV_TYPE: 'dev' | 'prod' | 'stage';
};

const app = new Hono<{ Bindings: Env }>();

app.use(prettyJSON())

app.notFound((c) => c.json({ status: 404, msg: 'Not Found' }))
app.route('v1/subject', subject);

export default app;

app.get('/ping', (c) => {
  return c.text('pong');
});

showRoutes(app, { verbose: true })
