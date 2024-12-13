import { AnonymousAuthenticationProvider } from "@microsoft/kiota-abstractions";
import {
  FetchRequestAdapter,
  HeadersInspectionHandler,
  KiotaClientFactory,
  ParametersNameDecodingHandler,
  RedirectHandler,
  RetryHandler,
  UserAgentHandler,
} from "@microsoft/kiota-http-fetchlibrary";
import {
  createPostsClient,
  PostsClient,
} from "../gpt_maa_client/postsClient.js";

// Create the API client
export const createClient = (baseurl: string | null = null): PostsClient => {
  // TODO: add support for Basic + Bearer authentication
  const authProvider = new AnonymousAuthenticationProvider();

  // Create request adapter using the fetch-based implementation
  //
  // turn OFF compression as it breaks the fastapi server - see https://github.com/microsoft/kiota-typescript/issues/1439
  const http = KiotaClientFactory.create(undefined, [
    new RetryHandler(),
    new RedirectHandler(),
    new ParametersNameDecodingHandler(),
    new UserAgentHandler(),
    new HeadersInspectionHandler(),
  ]);
  const adapter = new FetchRequestAdapter(
    authProvider,
    undefined,
    undefined,
    http
  );
  if (baseurl) adapter.baseUrl = baseurl;

  return createPostsClient(adapter);
};
