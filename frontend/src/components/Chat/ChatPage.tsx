import { useState } from 'react'
import { Layout } from 'antd'
import ConversationList from './ConversationList'
import ChatArea from './ChatArea'
import MessageInput from './MessageInput'
import NewConversationModal from './NewConversationModal'

const { Sider, Content } = Layout

export default function ChatPage() {
  const [newConvModalVisible, setNewConvModalVisible] = useState(false)

  return (
    <>
      <Layout style={{ height: 'calc(100vh - 64px)', background: '#fff' }}>
        <Sider width={300} style={{ background: '#fff', borderRight: '1px solid #f0f0f0' }}>
          <ConversationList onNewConversation={() => setNewConvModalVisible(true)} />
        </Sider>
        <Layout>
          <Content style={{ display: 'flex', flexDirection: 'column' }}>
            <div style={{ flex: 1, overflow: 'hidden' }}>
              <ChatArea />
            </div>
            <MessageInput />
          </Content>
        </Layout>
      </Layout>

      <NewConversationModal
        visible={newConvModalVisible}
        onClose={() => setNewConvModalVisible(false)}
      />
    </>
  )
}
