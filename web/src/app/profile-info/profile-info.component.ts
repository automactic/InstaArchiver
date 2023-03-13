import { Component, Input } from '@angular/core';
import { Observable, BehaviorSubject, tap } from 'rxjs';

import { ProfileWithDetails, ProfileService } from '../services/profile.service';
import { ListTasksResponse, TaskService } from '../services/task.service';


interface PostStatNode<T> {
  data: T;
  children?: PostStatNode<T>[];
  expanded?: boolean;
}

interface PostCount {
  year: string
  Q1: number
  Q2: number
  Q3: number
  Q4: number
}

@Component({
  selector: 'profile-info',
  templateUrl: './profile-info.component.html',
  styleUrls: ['./profile-info.component.scss']
})
export class ProfileInfoComponent {
  profileService: ProfileService
  taskService: TaskService
  
  @Input() username?: String
  allColumns = ['Year', 'Q4', 'Q3', 'Q2', 'Q1']
  stats: PostStatNode<PostCount>[] = []
  profile$: Observable<ProfileWithDetails | null> = new BehaviorSubject(null) 
  tasks$: Observable<ListTasksResponse | null> = new BehaviorSubject(null)

  constructor(profileService: ProfileService, taskService: TaskService) {
    this.profileService = profileService
    this.taskService = taskService
  }

  ngOnChanges(changes: any) {
    let username = changes.username.currentValue
    if (username) {
      this.profile$ = this.profileService.get(username).pipe(
        tap(profile => {
          this.stats = Object.keys(profile.counts).map(key => {
            let count = profile.counts[key] ?? {}
            return {
              data: {
                year: key,
                Q1: count['Q1'],
                Q2: count['Q2'],
                Q3: count['Q3'],
                Q4: count['Q4'],
              }
            }
          }).sort((lhs, rhs) => lhs.data.year < rhs.data.year ? 1 : -1)
        })
      )
      this.tasks$ = this.taskService.list(0, 5, username)
    } else {
      this.stats = []
      this.profile$ = new BehaviorSubject(null)
      this.tasks$ = new BehaviorSubject(null)
    }
  }
}
