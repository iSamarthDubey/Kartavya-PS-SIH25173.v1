import ChatWindow from '@/components/Chat/ChatWindow'

export default function ChatPage() {
  return (
    <div className="h-full overflow-hidden bg-synrgy-bg-900">
      <ChatWindow 
        className="h-full" 
        showHeader={true}
        title="SYNRGY | Conversational Assistant"
      />
    </div>
  )
}
