import 'dotenv/config';
import {StaticAuthProvider } from '@twurple/auth';
import {ChatClient} from '@twurple/chat';
import {Bot, createBotCommand} from '@twurple/easy-bot';

const clientId = 'gp762nuuoqcoxypju8c569th9wz7q5';
const accessToken = 'u305zbbnask0uxapbje50bq1zlr2p7';
const authProvider = new StaticAuthProvider(clientId, accessToken);

const channel = 'kahlipso_';

const chatClient = new ChatClient({
    authProvider,
    channels: [channel]
});

chatClient.connect();

chatClient.onMessage(async (channel, user, text, msg) => {
    console.log(`${user}: ${text}`);

    if(text.toLowerCase() === '!sr') {
        chatClient.say(channel, `@${user}, hello`);
    }
});