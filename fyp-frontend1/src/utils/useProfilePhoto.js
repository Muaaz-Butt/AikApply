import { useEffect, useState } from "react";
import api from "../api/axios";
import { getSession } from "./authStore";

export const PROFILE_UPDATED_EVENT = "profileUpdate";

// Uploaded files come back as "/media/..." paths; make them openable from the frontend
export const mediaUrl = (path) =>
  path && path.startsWith("/") ? `${api.defaults.baseURL}${path}` : path;

// One request shared by every component, per logged-in user
let cache = { user: null, promise: null };

function fetchPhoto(user) {
  if (cache.user !== user || !cache.promise) {
    cache = {
      user,
      promise: api.get("/student/profile/")
        .then(({ data }) => mediaUrl(data?.photo) || null)
        .catch(() => null),
    };
  }
  return cache.promise;
}

// Tell every component showing the photo to refetch it (call after saving the application)
export function notifyProfileUpdated() {
  cache = { user: null, promise: null };
  window.dispatchEvent(new Event(PROFILE_UPDATED_EVENT));
}

// Returns the URL of the photo uploaded in the application form, or null if there is none
export default function useProfilePhoto() {
  const user = getSession()?.username || null;
  const [photo, setPhoto] = useState(null);

  useEffect(() => {
    let cancelled = false;
    const load = () => {
      if (!user) { setPhoto(null); return; }
      fetchPhoto(user).then(url => { if (!cancelled) setPhoto(url); });
    };
    load();
    window.addEventListener(PROFILE_UPDATED_EVENT, load);
    return () => {
      cancelled = true;
      window.removeEventListener(PROFILE_UPDATED_EVENT, load);
    };
  }, [user]);

  return photo;
}
