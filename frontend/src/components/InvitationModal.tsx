import React from 'react';
import { TeamInvitationPanel } from './TeamInvitationPanel';

interface InvitationModalProps {
  isOpen: boolean;
  onClose: () => void;
  teamId: string;
  teamName: string;
  memberCount?: number;
  apiBase?: string;
}

export const InvitationModal: React.FC<InvitationModalProps> = ({
  isOpen,
  onClose,
  teamId,
  teamName,
  memberCount = 1,
  apiBase = '',
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="relative w-full max-w-xl">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white text-lg font-bold z-10 w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center"
        >
          ✕
        </button>
        <TeamInvitationPanel
          teamId={teamId}
          teamName={teamName}
          memberCount={memberCount}
          apiBase={apiBase}
        />
      </div>
    </div>
  );
};
export default InvitationModal;
