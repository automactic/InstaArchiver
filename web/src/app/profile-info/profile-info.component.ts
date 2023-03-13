import { Component, Input } from '@angular/core';
import { Observable, BehaviorSubject, switchMap, map } from 'rxjs';

import { Profile, ProfileService } from '../services/profile.service';
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
  
  @Input() profile?: Profile
  allColumns = ['Year', 'Q4', 'Q3', 'Q2', 'Q1']
  stats$: Observable<PostStatNode<PostCount>[]> = new BehaviorSubject([]) 
  tasks$: Observable<ListTasksResponse | null> = new BehaviorSubject(null)

  constructor(profileService: ProfileService, taskService: TaskService) {
    this.profileService = profileService
    this.taskService = taskService
  }

  ngOnChanges(changes: any) {
    let profile = changes.profile.currentValue
    if (profile) {
      this.stats$ = this.profileService.getStats(profile.username).pipe(
        map(stats => {
          if (stats.length > 0) {
            return Object.keys(stats[0].counts).map(key => {
              let count = stats[0].counts[key] ?? {}
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
          } else {
            return []
          }
        })
      )
      this.tasks$ = this.taskService.list(0, 5, profile.username)
    } else {
      this.stats$ = new BehaviorSubject([])
      this.tasks$ = new BehaviorSubject(null)
    }
  }
}
